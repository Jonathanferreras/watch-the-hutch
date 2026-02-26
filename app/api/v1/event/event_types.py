from enum import Enum
from pydantic import BaseModel

class EventSourceType(str, Enum):
    USER = "USER"
    DEVICE = "DEVICE"

class BridgeStatus(str, Enum):
    CLOSED = "CLOSED"
    OPENING = "OPENING"
    OPEN = "OPEN"
    CLOSING = "CLOSING"
    UNKNOWN = "UNKNOWN"

class BridgeStatePayload(BaseModel):
    status: BridgeStatus
    confidence: str

class DeviceTelemetryPayload(BaseModel):
    cpu: str
    ram: str
    temperature: str
    voltage: str
    camera: str
