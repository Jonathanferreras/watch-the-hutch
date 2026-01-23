"""Dependency injection for admin module."""
from fastapi import Depends, HTTPException, status, Request
from app.api.v1.admin.admin_repository import AdminRepository
from app.api.v1.admin.admin_service import AdminService
from app.api.v1.admin.admin_model import AdminUser
from app.security import verify_admin_token

def get_repository() -> AdminRepository:
    return AdminRepository()

def get_service(
    repository: AdminRepository = Depends(get_repository)
) -> AdminService:
    return AdminService(repository)

def get_current_admin(
    request: Request,
    service: AdminService = Depends(get_service)
) -> AdminUser:
    """
    Dependency to get the current authenticated admin from the session cookie.
    Raises HTTPException if not authenticated.
    """
    # Get token from cookie
    token = request.cookies.get("admin_session")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    # Verify token
    payload = verify_admin_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    # Get admin from database
    admin_id = payload.get("admin_id")
    if not admin_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    admin = service.repository.get_by_id(admin_id)
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
