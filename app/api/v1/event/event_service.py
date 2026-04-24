import logging
from typing import List
from app.api.v1.event.event_model import Event
from app.api.v1.event.event_types import EventSourceType, EventPayloadType
from app.api.v1.event.event_repository import EventRepository
from app.api.v1.state.state_service import StateService

logger = logging.getLogger(__name__)

class EventService:
    def __init__(self, repository: EventRepository = None, state_service: StateService = None):
        self.repository = repository or EventRepository()
        self.state_service = state_service or StateService()

    def create_event(self, event: Event) -> Event:
        created_event = self.repository.create_event(event)
        
        try:
            if created_event.payloadType != EventPayloadType.BRIDGE_STATE:
                return created_event

            current_state = self.state_service.get_current_state()

            if created_event.source_type == EventSourceType.USER:
                self.state_service.update_current_state(created_event, can_update=False)
            elif (
                created_event.source_type == EventSourceType.DEVICE
                and (current_state is None or current_state.can_update)
            ):
                self.state_service.update_current_state(created_event)

        except Exception as e:
            logger.error(
                f"Failed to update state after creating event {created_event.event_id}: {e}",
                exc_info=True
            )
            # Consider whether to raise here or continue - depends on your requirements
            # For now, we log and continue to ensure event persistence
        
        return created_event

    def get_events(self) -> List[Event]:
        return self.repository.get_events()
    
    def latest_event_by_type(self, event_type: EventPayloadType) -> Event:
        return self.repository.get_latest_event_by_type(event_type)
