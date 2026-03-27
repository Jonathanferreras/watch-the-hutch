"""Dependency injection for auth module."""
from fastapi import Depends, HTTPException, Request, status
from app.api.v1.auth.auth_service import AuthService
from app.api.v1.admin.admin_repository import AdminRepository
from app.api.v1.admin.admin_service import AdminService
from app.api.v1.admin.admin_model import AdminUser

def get_repository() -> AdminRepository:
    return AdminRepository()

def get_admin_service(
    repository: AdminRepository = Depends(get_repository)
) -> AdminService:
    return AdminService(repository)

def get_auth_service() -> AuthService:
    return AuthService()

def get_current_admin(
    request: Request,
    admin_service: AdminService = Depends(get_admin_service),
    auth_service: AuthService = Depends(get_auth_service),
) -> AdminUser:
    token = request.cookies.get("admin_access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    payload = auth_service.decode_jwt(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token or expired token"
        )

    admin_id = payload.get("user_id")

    if not admin_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    admin = admin_service.repository.get_by_id(admin_id)

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin user not found"
        )

    if not admin.is_active:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin account is inactive"
        )

    return admin
