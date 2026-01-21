import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from app.api.v1.state.state_service import StateService
from app.api.v1.state.state_model import State
from app.api.v1.state.dependencies import get_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/state")
def get_current_state(service: StateService = Depends(get_service)) -> Optional[State]:
    try:
        return service.get_current_state()
    except Exception as e:
        logger.error(f"Error getting current state: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting current state: {str(e)}")


@router.post("/state")
def create_state(state: State, service: StateService = Depends(get_service)) -> State:
    try:
        return service.create_state(state)
    except Exception as e:
        logger.error(f"Error creating state: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error creating current state: {str(e)}")
