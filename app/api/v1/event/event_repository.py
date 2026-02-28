from typing import Optional, List, Union
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, JSON, Session, select
from sqlalchemy.engine import Engine
from pydantic import BaseModel
from app.api.v1.event.event_model import Event
from app.api.v1.event.event_types import BridgeStatePayload, DeviceTelemetryPayload, EventSourceType, EventPayloadType
from app.db import get_engine


class EventSQLModel(SQLModel, table=True):
    __tablename__ = "event"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: str = Field(unique=True, index=True)
    source_id: str = Field(index=True)
    source_type: EventSourceType = Field(index=True)
    payload: Union[BridgeStatePayload, DeviceTelemetryPayload] = Field(sa_column=Column(JSON), default_factory=dict)
    # payloadType: EventPayloadType = Field(index=True)
    timestamp: datetime = Field(index=True)

    @staticmethod
    def _serialize_payload(payload: Union[BridgeStatePayload, DeviceTelemetryPayload, dict]) -> dict:
        if isinstance(payload, BaseModel):
            return payload.model_dump()
        return payload

    @staticmethod
    def _deserialize_payload(payload: Union[dict, BridgeStatePayload, DeviceTelemetryPayload]) -> Union[BridgeStatePayload, DeviceTelemetryPayload]:
        if isinstance(payload, dict):
            if "status" in payload:
                return BridgeStatePayload(**payload)
            return DeviceTelemetryPayload(**payload)
        return payload
    
    def to_domain(self) -> Event:
        return Event(
            event_id=self.event_id,
            source_id=self.source_id,
            source_type=self.source_type,
            payload=self._deserialize_payload(self.payload),
            # payloadType=self.payloadType,
            timestamp=self.timestamp
        )
    
    @classmethod
    def from_domain(cls, event: Event) -> "EventSQLModel":
        return cls(
            event_id=event.event_id,
            source_id=event.source_id,
            source_type=event.source_type,
            payload=cls._serialize_payload(event.payload),
            # payloadType=event.payloadType,
            timestamp=event.timestamp
        )

class EventRepository:
    def __init__(self, engine: Engine = None):
        self.engine = engine or get_engine()

    def _get_session(self) -> Session:
        """Create and return a database session."""
        return Session(self.engine)

    def create_event(self, event: Event) -> Event:
        with self._get_session() as session:
            event_sql_model = EventSQLModel.from_domain(event)
            session.add(event_sql_model)
            session.commit()
            session.refresh(event_sql_model)
            return event_sql_model.to_domain()
    
    def get_events(self) -> List[Event]:
        with self._get_session() as session:
            statement = select(EventSQLModel).order_by(EventSQLModel.timestamp.desc())
            results = session.exec(statement).all()
            return [event.to_domain() for event in results]

    def get_latest_event(self) -> Optional[Event]:
        with self._get_session() as session:
            statement = select(EventSQLModel).order_by(EventSQLModel.timestamp.desc()).limit(1)
            result = session.exec(statement).first()
            return result.to_domain() if result else None
