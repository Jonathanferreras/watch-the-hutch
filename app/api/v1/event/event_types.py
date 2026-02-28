from enum import Enum
from pydantic import BaseModel

class EventSourceType(str, Enum):
    USER = "USER"
    DEVICE = "DEVICE"

class EventPayloadType(str, Enum):
    BRIDGE_STATE = "BRIDGE_STATE"
    DEVICE_TELEMETRY = "DEVICE_TELEMETRY"

class BridgeStatus(str, Enum):
    CLOSED = "CLOSED"
    OPENING = "OPENING"
    OPEN = "OPEN"
    CLOSING = "CLOSING"
    UNKNOWN = "UNKNOWN"

class CameraViewStatus(str, Enum):
    CLEAR = "CLEAR"
    PARTIAL = "PARTIAL"
    BLOCKED = "BLOCKED"

class BridgeStatePayload(BaseModel):
    status: BridgeStatus
    confidence: str

class DeviceTelemetryPayload(BaseModel):
    cpu: str
    ram: str
    temperature: str
    voltage: str
    camera_connected: bool
    camera_view_status: CameraViewStatus
    is_online: bool
