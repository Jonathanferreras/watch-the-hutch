import logging
from fastapi import APIRouter, HTTPException, Depends, status, Response
from fastapi.responses import JSONResponse
from app.api.v1.admin.admin_service import AdminService
from app.api.v1.admin.admin_model import AdminUser, AdminLogin, AdminCreate
from app.api.v1.admin.dependencies import get_service, get_current_admin
from app.security import create_admin_token

logger = logging.getLogger(__name__)
router = APIRouter()

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
