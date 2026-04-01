import json
import logging
import uuid
from datetime import datetime

from app.api.v1.event.event_model import Event
from app.api.v1.event.event_service import EventService
from app.api.v1.event.event_types import BridgeStatePayload, DeviceTelemetryPayload, EventSourceType, EventPayloadType
from app.mqtt.topics import DEVICE_TELEMETRY

logger = logging.getLogger("event_manager")
logger.setLevel(logging.DEBUG)


def _parse_payload(data: dict) -> BridgeStatePayload | DeviceTelemetryPayload:
    """Parse JSON dict into the correct payload type."""
    if "status" in data and "confidence" in data:
        return BridgeStatePayload(**data)
    return DeviceTelemetryPayload(**data)


async def process_mqtt_message(topic: str, payload: str):
    logger.info(f"Processing MQTT message from {topic}: {payload}")

    if topic != DEVICE_TELEMETRY:
        return

    try:
        data = json.loads(payload)
        payload_obj = _parse_payload(data)
        payload_type = None

        if topic == DEVICE_TELEMETRY:
            payload_type = EventPayloadType.DEVICE_TELEMETRY
        else:
            logger.error(f"Unrecognized payload type!")
            return

        event = Event(
            event_id=str(uuid.uuid4()),
            source_id=data.get("source_id", "mqtt"),
            source_type=EventSourceType.DEVICE,
            payload=payload_obj,
            payloadType=payload_type,
            timestamp=datetime.utcnow(),
        )

        service = EventService()
        service.create_event(event)

        logger.info("Event created from MQTT message")
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
        logger.error(f"Invalid MQTT payload: {e}")