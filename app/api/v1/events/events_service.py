from typing import List
from app.api.v1.events.events_model import Event
from app.api.v1.events.events_repository import EventsRepository

class EventsService:
    def __init__(self, repository: EventsRepository = None):
        self.repository = repository or EventsRepository()

    def create_event(self, event: Event) -> Event:
        return self.repository.create_event(event)

    def get_events(self) -> List[Event]:
        return self.repository.get_events()