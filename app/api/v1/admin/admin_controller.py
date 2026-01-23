import logging
from fastapi import APIRouter, HTTPException, Depends, status, Response
from fastapi.responses import JSONResponse
from app.api.v1.admin.admin_service import AdminService
from app.api.v1.admin.admin_model import AdminUser, AdminLogin, AdminCreate
from app.api.v1.admin.dependencies import get_service, get_current_admin
from app.security import create_admin_token

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/login")
def login(
    credentials: AdminLogin,
    response: Response,
    service: AdminService = Depends(get_service)
) -> dict:
    """
    Authenticate an admin user and set a session cookie.
    """
    try:
        admin = service.authenticate(credentials.username, credentials.password)
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Create token
        token = create_admin_token(admin.id, admin.username, expires_in_hours=2)
        
        # Set secure cookie
        response.set_cookie(
            key="admin_session",
            value=token,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax",
            max_age=7200  # 2 hours in seconds
        )
        
        return {
            "message": "Login successful",
            "admin": {
                "id": admin.id,
                "username": admin.username,
                "role": admin.role.value
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during login: {str(e)}"
        )

@router.post("/logout")
def logout(response: Response) -> dict:
    """
    Logout by clearing the session cookie.
    """
    response.delete_cookie(key="admin_session")
    return {"message": "Logout successful"}

@router.get("/me")
def get_current_user(
    current_admin: AdminUser = Depends(get_current_admin)
) -> AdminUser:
    """
    Get the current authenticated admin user.
    """
    return current_admin

@router.post("/users")
def create_admin_user(
    payload: AdminCreate,
    current_admin: AdminUser = Depends(get_current_admin),
    service: AdminService = Depends(get_service)
) -> AdminUser:
    """
    Create a new admin user. Requires ADMIN role.
    """
    # Check if current admin has ADMIN role
    if current_admin.role.value != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only ADMIN role can create admin users"
        )
    
    try:
        return service.create_admin(payload)
    except Exception as e:
        logger.error(f"Error creating admin user: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating admin user: {str(e)}"
        )
