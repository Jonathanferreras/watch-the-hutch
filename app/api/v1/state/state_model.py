from enum import Enum
from datetime import datetime
from pydantic import BaseModel
from app.api.v1.events.events_model import BridgeState


class State(BaseModel):
    state_id: str
    bridge_state: BridgeState
    timestamp: datetime
    last_event_id: str

    class Config:
        from_attributes = True
