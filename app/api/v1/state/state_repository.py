from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Session, select
from sqlalchemy import ForeignKey, Column, String
from sqlalchemy.engine import Engine
from app.api.v1.state.state_model import State
from app.api.v1.events.events_model import BridgeState
from app.db import get_engine


class StateSQLModel(SQLModel, table=True):
    __tablename__ = "state"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    state_id: str = Field(index=True)
    bridge_state: BridgeState = Field(index=True)
    timestamp: datetime = Field(index=True)
    last_event_id: str = Field(
        sa_column=Column(String, ForeignKey("events.event_id"), index=True)
    )
    
    def to_domain(self) -> State:
        return State(
            state_id=self.state_id,
            bridge_state=self.bridge_state,
            timestamp=self.timestamp,
            last_event_id=self.last_event_id
        )
    
    @classmethod
    def from_domain(cls, state: State) -> "StateSQLModel":
        return cls(
            state_id=state.state_id,
            bridge_state=state.bridge_state,
            timestamp=state.timestamp,
            last_event_id=state.last_event_id
        )


class StateRepository:
    def __init__(self, engine: Engine = None):
        self.engine = engine or get_engine()

    def _get_session(self) -> Session:
        """Create and return a database session."""
        return Session(self.engine)

    def create_state(self, state: State) -> State:
        with self._get_session() as session:
            state_sql_model = StateSQLModel.from_domain(state)
            session.add(state_sql_model)
            session.commit()
            session.refresh(state_sql_model)
            
            return state_sql_model.to_domain()
    
    def get_current_state(self) -> Optional[State]:
        with self._get_session() as session:
            statement = select(StateSQLModel).order_by(StateSQLModel.timestamp.desc())
            results = session.exec(statement).all()
            
            if not results:
                return None
            
            return results[0].to_domain()
    
    def update_current_state(self, state: State) -> State:
        with self._get_session() as session:
            statement = select(StateSQLModel).order_by(StateSQLModel.timestamp.desc())
            results = session.exec(statement).all()
            
            if results:
                # Update existing state
                existing_state = results[0]
                existing_state.state_id = state.state_id
                existing_state.bridge_state = state.bridge_state
                existing_state.timestamp = state.timestamp
                existing_state.last_event_id = state.last_event_id
                session.add(existing_state)
                session.commit()
                session.refresh(existing_state)

                return existing_state.to_domain()
            else:
                # Create new state if none exists
                state_sql_model = StateSQLModel.from_domain(state)
                session.add(state_sql_model)
                session.commit()
                session.refresh(state_sql_model)
                
                return state_sql_model.to_domain()