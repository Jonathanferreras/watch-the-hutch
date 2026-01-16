from enum import Enum
from datetime import datetime
from pydantic import BaseModel


class BridgeState(str, Enum):
    CLOSED = "CLOSED"
    OPENING = "OPENING"
    OPEN = "OPEN"
    CLOSING = "CLOSING"
    UNKNOWN = "UNKNOWN"


class Event(BaseModel):
    event_id: str
    source_device_id: str
    bridge_state: BridgeState
    bridge_confidence: float
    timestamp: datetime

    class Config:
        from_attributes = True
