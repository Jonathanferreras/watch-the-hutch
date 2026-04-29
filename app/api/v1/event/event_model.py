from datetime import datetime
from pydantic import BaseModel
from app.api.v1.event.event_types import EventSourceType, EventPayloadType, BridgeStatePayload, DeviceTelemetryPayload, BoatDetectionPayload

class Event(BaseModel):
    event_id: str
    source_id: str
    source_type: EventSourceType
    payload: BridgeStatePayload | DeviceTelemetryPayload | BoatDetectionPayload
    payloadType: EventPayloadType
    timestamp: datetime

    class Config:
        from_attributes = True
