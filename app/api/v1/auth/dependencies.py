"""Dependency injection for auth module."""
from fastapi import Depends
from app.api.v1.auth.auth_service import AuthService
from app.api.v1.admin.admin_repository import AdminRepository
from app.api.v1.admin.admin_service import AdminService

def get_repository() -> AdminRepository:
    return AdminRepository()

def get_admin_service(
    repository: AdminRepository = Depends(get_repository)
) -> AdminService:
    return AdminService(repository)

def get_auth_service() -> AuthService:
    return AuthService()