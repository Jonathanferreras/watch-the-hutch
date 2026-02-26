"""Dependency injection for event module."""
from fastapi import Depends
from app.api.v1.event.event_repository import EventRepository
from app.api.v1.event.event_service import EventService
from app.api.v1.state.state_service import StateService
from app.api.v1.state.dependencies import get_service as get_state_service


def get_repository() -> EventRepository:
    return EventRepository()

def get_service(
    repository: EventRepository = Depends(get_repository),
    state_service: StateService = Depends(get_state_service)
) -> EventService:
    return EventService(repository, state_service)
