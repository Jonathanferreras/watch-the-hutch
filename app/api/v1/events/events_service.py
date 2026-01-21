import logging
from typing import List
from app.api.v1.events.events_model import Event
from app.api.v1.events.events_repository import EventsRepository
from app.api.v1.state.state_service import StateService

logger = logging.getLogger(__name__)

class EventsService:
    def __init__(self, repository: EventsRepository = None, state_service: StateService = None):
        self.repository = repository or EventsRepository()
        self.state_service = state_service or StateService()

    def create_event(self, event: Event) -> Event:
        created_event = self.repository.create_event(event)
        
        try:
            self.state_service.update_current_state(created_event)
        except Exception as e:
            # Log error but don't fail the request - event is already persisted
            logger.error(
                f"Failed to update state after creating event {created_event.event_id}: {e}",
                exc_info=True
            )
            # Consider whether to raise here or continue - depends on your requirements
            # For now, we log and continue to ensure event persistence
        
        return created_event

    def get_events(self) -> List[Event]:
        return self.repository.get_events()