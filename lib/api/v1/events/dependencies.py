"""Dependency injection for events module."""
from fastapi import Depends
from lib.api.v1.events.events_repository import EventsRepository
from lib.api.v1.events.events_service import EventsService


def get_repository() -> EventsRepository:
    return EventsRepository()

def get_service(repository: EventsRepository = Depends(get_repository)) -> EventsService:
    return EventsService(repository)

