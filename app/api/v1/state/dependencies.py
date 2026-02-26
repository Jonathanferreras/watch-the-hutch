"""Dependency injection for state module."""
from fastapi import Depends
from app.api.v1.state.state_repository import StateRepository
from app.api.v1.state.state_service import StateService
from app.api.v1.event.event_repository import EventRepository


def get_repository() -> StateRepository:
    return StateRepository()

def get_event_repository() -> EventRepository:
    return EventRepository()

def get_service(
    repository: StateRepository = Depends(get_repository),
    event_repository: EventRepository = Depends(get_event_repository),
) -> StateService:
    return StateService(repository, event_repository)
