import logging
from fastapi import APIRouter, HTTPException, Depends, status, Response
from app.api.v1.auth.auth_service import AuthService
from app.api.v1.admin.admin_service import AdminService
from app.api.v1.admin.admin_model import AdminLogin
from app.api.v1.auth.dependencies import get_admin_service, get_auth_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/login")
def login(
    credentials: AdminLogin,
    admin_service: AdminService = Depends(get_admin_service),
    auth_service: AuthService = Depends(get_auth_service)
) -> dict:
    """
    Authenticate a user and return a jwt access token
    """
    admin = admin_service.authenticate(credentials.username, credentials.password)
    
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    return auth_service.sign_jwt(admin.username)


@router.post("/logout")
def logout(response: Response) -> dict:
    """
    Logout
    """