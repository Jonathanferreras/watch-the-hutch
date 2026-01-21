import uuid
from typing import Optional
from app.api.v1.state.state_model import State
from app.api.v1.state.state_repository import StateRepository
from app.api.v1.events.events_model import Event

class StateService:
    def __init__(self, repository: StateRepository = None):
        self.repository = repository or StateRepository()

    def create_state(self, state: State) -> State:
        return self.repository.create_state(state)

    def get_current_state(self) -> Optional[State]:
        return self.repository.get_current_state()

    def update_current_state(self, event: Event) -> State:
        current_state = self.get_current_state()
        
        # Idempotency check: if this event was already processed, return current state
        if current_state and current_state.last_event_id == event.event_id:
            return current_state
        
        new_state = State(
            state_id=str(uuid.uuid4()),
            bridge_state=event.bridge_state,
            timestamp=event.timestamp,
            last_event_id=event.event_id
        )
        return self.repository.update_current_state(new_state)
