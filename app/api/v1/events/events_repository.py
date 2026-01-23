from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Session, select
from sqlalchemy.engine import Engine
from app.api.v1.events.events_model import Event, BridgeState
from app.db import get_engine


class EventSQLModel(SQLModel, table=True):
    __tablename__ = "events"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: str = Field(unique=True, index=True)
    source_device_id: str = Field(index=True)
    bridge_state: BridgeState = Field(index=True)
    bridge_confidence: float = Field(index=True)
    timestamp: datetime = Field(index=True)
    
    def to_domain(self) -> Event:
        return Event(
            event_id=self.event_id,
            source_device_id=self.source_device_id,
            bridge_state=self.bridge_state,
            bridge_confidence=self.bridge_confidence,
            timestamp=self.timestamp
        )
    
    @classmethod
    def from_domain(cls, event: Event) -> "EventSQLModel":
        return cls(
            event_id=event.event_id,
            source_device_id=event.source_device_id,
            bridge_state=event.bridge_state,
            bridge_confidence=event.bridge_confidence,
            timestamp=event.timestamp
        )


class EventsRepository:
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