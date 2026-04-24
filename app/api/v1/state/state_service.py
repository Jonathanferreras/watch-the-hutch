import uuid
import datetime
from typing import Optional
from app.api.v1.state.state_model import State, StateUpdateRequest
from app.api.v1.event.event_model import Event
from app.api.v1.state.state_repository import StateRepository
from app.api.v1.event.event_repository import EventRepository
from app.api.v1.event.event_types import BridgeStatePayload, EventSourceType, EventPayloadType

class StateService:
    def __init__(self, repository: StateRepository = None, event_repository: EventRepository = None):
        self.repository = repository or StateRepository()
        self.event_repository = event_repository or EventRepository()

    def create_state(self, state_update: StateUpdateRequest) -> State:
        event = Event(
            event_id=str(uuid.uuid4()),
            source_id="admin",
            source_type=EventSourceType.USER,
            payload=BridgeStatePayload(status=state_update.bridge_state, confidence="manual"),
            payloadType=EventPayloadType.BRIDGE_STATE,
            timestamp=datetime.datetime.utcnow(),
        )
        created_event = self.event_repository.create_event(event)
        return self.update_current_state(created_event, can_update=False)

    def get_current_state(self) -> Optional[State]:
        return self.repository.get_current_state()
    
    def toggle_updates(self, value: bool) -> Optional[State]:
        current_state = self.get_current_state()
        if current_state:
            new_state = State(
                state_id=current_state.state_id,
                bridge_state=current_state.bridge_state,
                timestamp=current_state.timestamp,
                last_event_id=current_state.last_event_id,
                can_update=value
            )
            updated_state = self.repository.update_current_state(new_state)
        else:
            updated_state = None

        return updated_state


    def update_current_state(self, event: Event, can_update: bool = True) -> State:
        current_state = self.get_current_state()
        
        # Idempotency check: if this event was already processed, return current state
        if current_state and current_state.last_event_id == event.event_id:
            return current_state

        if current_state and not current_state.can_update and event.source_type == EventSourceType.DEVICE:
            return current_state

        payload = event.payload
        bridge_state = payload.status if isinstance(payload, BridgeStatePayload) else getattr(payload, "status", None)

        if bridge_state is None:
            raise ValueError("Event payload missing bridge status")

        if event.source_type == EventSourceType.USER:
            can_update = False

        new_state = State(
            state_id=str(uuid.uuid4()),
            bridge_state=bridge_state,
            timestamp=event.timestamp,
            last_event_id=event.event_id,
            can_update=can_update
        )

        return self.repository.update_current_state(new_state)
