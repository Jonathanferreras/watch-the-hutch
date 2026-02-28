from datetime import datetime
from pydantic import BaseModel
from app.api.v1.event.event_types import EventSourceType, EventPayloadType, BridgeStatePayload, DeviceTelemetryPayload

class Event(BaseModel):
    event_id: str
    source_id: str
    source_type: EventSourceType
    payload: BridgeStatePayload | DeviceTelemetryPayload
    #payloadType: EventPayloadType <- TODO: update database to have this column
    timestamp: datetime

    class Config:
        from_attributes = True
