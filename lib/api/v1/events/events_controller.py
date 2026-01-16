import logging
from typing import List
from fastapi import APIRouter, HTTPException, Depends
from lib.api.v1.events.events_service import EventsService
from lib.api.v1.events.events_model import Event
from lib.api.v1.events.dependencies import get_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/events")
def get_events(service: EventsService = Depends(get_service)) -> List[Event]:
    try:
        return service.get_events()
    except Exception as e:
        logger.error(f"Error getting events: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting events: {str(e)}")


@router.post("/events")
def create_event(event: Event, service: EventsService = Depends(get_service)) -> Event:
    try:
        return service.create_event(event)
    except Exception as e:
        logger.error(f"Error creating event: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error creating event: {str(e)}")
