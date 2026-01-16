import os
from sqlmodel import SQLModel, create_engine

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://{os.getenv('POSTGRES_USER', 'postgres')}:{os.getenv('POSTGRES_PASSWORD', 'postgres')}@{os.getenv('POSTGRES_HOST', 'localhost')}:{os.getenv('POSTGRES_PORT', '5432')}/{os.getenv('POSTGRES_DB', 'watchthehutch')}"
)

engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    # Import models here to avoid circular imports
    # This ensures models are registered with SQLModel.metadata
    from app.api.v1.events.events_repository import EventSQLModel
    SQLModel.metadata.create_all(engine)


def get_engine():
    return engine

