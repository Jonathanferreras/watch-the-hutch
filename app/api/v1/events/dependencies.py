"""Dependency injection for events module."""
from fastapi import Depends
from app.api.v1.events.events_repository import EventsRepository
from app.api.v1.events.events_service import EventsService
from app.api.v1.state.state_service import StateService
from app.api.v1.state.dependencies import get_service as get_state_service


def get_repository() -> EventsRepository:
    return EventsRepository()

def get_service(
    repository: EventsRepository = Depends(get_repository),
    state_service: StateService = Depends(get_state_service)
) -> EventsService:
    return EventsService(repository, state_service)
