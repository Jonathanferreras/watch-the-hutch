import logging
import os
from fastapi import APIRouter, HTTPException, Depends, status, Response
from app.api.v1.auth.auth_service import AuthService
from app.api.v1.admin.admin_service import AdminService
from app.api.v1.admin.admin_model import AdminLogin, AdminUser
from app.api.v1.auth.dependencies import get_admin_service, get_auth_service, get_current_admin

logger = logging.getLogger(__name__)
router = APIRouter()
secure_cookie = os.getenv("AUTH_COOKIE_SECURE", "false").lower() == "true"

@router.post("/login")
def login(
    credentials: AdminLogin,
    response: Response,
    admin_service: AdminService = Depends(get_admin_service),
    auth_service: AuthService = Depends(get_auth_service)
) -> dict:
    """
    Authenticate a user and set an auth cookie.
    """
    admin = admin_service.authenticate(credentials.username, credentials.password)
    
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    token = auth_service.sign_jwt(admin.id)["access_token"]

    response.set_cookie(
        key="admin_access_token",
        value=token,
        httponly=True,
        secure=secure_cookie,
        samesite="lax",
        max_age=600,
    )

    return {
        "admin": admin.model_dump(),
    }


@router.get("/me")
def get_current_user(
    current_admin: AdminUser = Depends(get_current_admin)
) -> AdminUser:
    """
    Get the current authenticated admin user.
    """
    return current_admin


@router.post("/logout")
def logout(response: Response) -> dict:
    """
    Logout
    """
    response.delete_cookie(key="admin_access_token")
    return {"message": "Logout successful"}
