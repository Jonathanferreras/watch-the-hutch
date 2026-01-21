"""Dependency injection for events module."""
from fastapi import Depends
from app.api.v1.state.state_repository import StateRepository
from app.api.v1.state.state_service import StateService


def get_repository() -> StateRepository:
    return StateRepository()

def get_service(repository: StateRepository = Depends(get_repository)) -> StateService:
    return StateService(repository)
