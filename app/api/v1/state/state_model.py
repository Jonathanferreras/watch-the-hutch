from enum import Enum
from datetime import datetime
from pydantic import BaseModel
from app.api.v1.event.event_types import BridgeStatus


class State(BaseModel):
    state_id: str
    bridge_state: BridgeStatus
    timestamp: datetime
    last_event_id: str
    can_update: bool = True

    class Config:
        from_attributes = True
