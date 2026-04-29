import os
import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
import smtplib
import mimetypes
from email.message import EmailMessage

from app.api.v1.event.event_model import Event
from app.api.v1.event.event_service import EventService
from app.api.v1.event.event_types import BridgeStatePayload, DeviceTelemetryPayload, BoatDetectionPayload, EventSourceType, EventPayloadType
from app.mqtt.topics import BOAT_DETECTION, BOAT_DETECTION_IMAGE, DEVICE_TELEMETRY

logger = logging.getLogger("event_manager")
logger.setLevel(logging.DEBUG)
CAPTURES_DIR = Path("captures")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_TIMEOUT_SECONDS = float(os.getenv("SMTP_TIMEOUT_SECONDS", "10"))
EMAIL_FROM = os.getenv("EMAIL_FROM", SMTP_USERNAME or "")
EMAIL_TO = os.getenv("EMAIL_TO")


def _parse_payload(topic: str, data: dict) -> BridgeStatePayload | DeviceTelemetryPayload | BoatDetectionPayload:
    """Parse JSON dict into the correct payload type for the MQTT topic."""
    if topic == BOAT_DETECTION:
        return BoatDetectionPayload(**data)
    if "status" in data and "confidence" in data:
        return BridgeStatePayload(**data)
    return DeviceTelemetryPayload(**data)


async def process_mqtt_message(topic: str, payload: str):
    logger.info(f"Processing MQTT message from {topic}: {payload}")

    if topic not in {DEVICE_TELEMETRY, BOAT_DETECTION}:
        return

    try:
        data = json.loads(payload)
        payload_obj = _parse_payload(topic, data)
        payload_type = None

        if topic == DEVICE_TELEMETRY:
            payload_type = EventPayloadType.DEVICE_TELEMETRY
        elif topic == BOAT_DETECTION:
            payload_type = EventPayloadType.BOAT_DETECTION
        else:
            logger.error(f"Unrecognized payload type!")
            return

        source_id = data.get("source_id") or data.get("source") or "mqtt"
        timestamp = datetime.now(timezone.utc)

        if topic == BOAT_DETECTION:
            timestamp = payload_obj.published_at

        event = Event(
            event_id=str(uuid.uuid4()),
            source_id=source_id,
            source_type=EventSourceType.DEVICE,
            payload=payload_obj,
            payloadType=payload_type,
            timestamp=timestamp,
        )

        service = EventService()
        service.create_event(event)

        logger.info("Event created from MQTT message")
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
        logger.error(f"Invalid MQTT payload: {e}")


async def process_mqtt_image(topic: str, payload: bytes) -> Path | None:
    if not topic.startswith(f"{BOAT_DETECTION_IMAGE}/"):
        return None

    if not payload:
        logger.warning("Received empty payload for boat detection image topic %s", topic)
        return None

    image_id = topic.removeprefix(f"{BOAT_DETECTION_IMAGE}/").strip()
    if not image_id:
        logger.warning("Boat detection image topic missing image id: %s", topic)
        return None

    CAPTURES_DIR.mkdir(parents=True, exist_ok=True)
    image_path = CAPTURES_DIR / f"{image_id}.jpg"
    image_path.write_bytes(payload)
    logger.info("Saved boat detection image to %s", image_path)

    if EMAIL_TO and SMTP_USERNAME and SMTP_PASSWORD:
        await asyncio.to_thread(email_image, image_path)
    else:
        logger.info("Skipping detection email because SMTP settings are incomplete")

    return image_path

def email_image(image_path: Path) -> None:
    msg = EmailMessage()
    msg['Subject'] = "WTH: Boat Detected"
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO
    msg.set_content("See attached image.")

    with open(image_path, 'rb') as f:
        file_data = f.read()
        ctype, _ = mimetypes.guess_type(str(image_path))
        maintype, subtype = (ctype or 'application/octet-stream').split('/', 1)
        msg.add_attachment(file_data, maintype=maintype, subtype=subtype, filename=image_path.name)

    try:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=SMTP_TIMEOUT_SECONDS) as smtp:
            smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
            smtp.send_message(msg)
        logger.info("Sent detection email for %s", image_path.name)
    except smtplib.SMTPException as e:
        logger.error("Failed to send detection email for %s: %s", image_path.name, e)
    except OSError as e:
        logger.error("SMTP connection failed for %s: %s", image_path.name, e)
