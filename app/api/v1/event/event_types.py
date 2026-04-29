from enum import Enum
from datetime import datetime
from pydantic import BaseModel

class EventSourceType(str, Enum):
    USER = "USER"
    DEVICE = "DEVICE"

class EventPayloadType(str, Enum):
    BRIDGE_STATE = "BRIDGE_STATE"
    DEVICE_TELEMETRY = "DEVICE_TELEMETRY"
    BOAT_DETECTION = "BOAT_DETECTION"

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
    camera_view_status: CameraViewStatus | None #TODO: Remove None once this feature is built.
    is_online: bool


class BoatDetectionPayload(BaseModel):
    direction: str
    detected_at: datetime
    published_at: datetime
    confidence: float
    source: str
    center_x: float
    image_topic: str
    image_id: str
