from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Column, String, Session, select
from sqlalchemy.engine import Engine
from app.api.v1.admin.admin_model import AdminUser, AdminRole
from app.db import get_engine

class AdminUserSQLModel(SQLModel, table=True):
    __tablename__ = "admin_users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password_hash: str = Field(sa_column=Column(String, nullable=False))
    role: AdminRole = Field(default=AdminRole.VIEWER, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login_at: Optional[datetime] = Field(default=None)
    is_active: bool = Field(default=True)

    def to_domain(self) -> AdminUser:
        return AdminUser(
            id=self.id,
            username=self.username,
            role=self.role,
            created_at=self.created_at,
            updated_at=self.updated_at,
            last_login_at=self.last_login_at,
            is_active=self.is_active
        )

    @classmethod
    def from_domain(cls, admin_user: AdminUser, password_hash: str) -> "AdminUserSQLModel":
        return cls(
            id=admin_user.id,
            username=admin_user.username,
            password_hash=password_hash,
            role=admin_user.role,
            created_at=admin_user.created_at,
            updated_at=admin_user.updated_at,
            last_login_at=admin_user.last_login_at,
            is_active=admin_user.is_active
        )

class AdminRepository:
    def __init__(self, engine: Engine = None):
        self.engine = engine or get_engine()

    def _get_session(self) -> Session:
        return Session(self.engine)

    def get_by_username(self, username: str) -> Optional[AdminUserSQLModel]:
        """Get an admin user by username, including password_hash for verification."""
        with self._get_session() as session:
            statement = select(AdminUserSQLModel).where(AdminUserSQLModel.username == username)
            result = session.exec(statement).first()
            if result:
                return result
            return None

    def get_by_id(self, admin_id: int) -> Optional[AdminUser]:
        """Get an admin user by ID."""
        with self._get_session() as session:
            statement = select(AdminUserSQLModel).where(AdminUserSQLModel.id == admin_id)
            result = session.exec(statement).first()
            if result:
                return result.to_domain()
            return None

    def create_admin_user(self, admin_user: AdminUser, password_hash: str) -> AdminUser:
        """Create a new admin user with the provided password hash."""
        with self._get_session() as session:
            admin_user_sql_model = AdminUserSQLModel.from_domain(admin_user, password_hash)
            session.add(admin_user_sql_model)
            session.commit()
            session.refresh(admin_user_sql_model)
            return admin_user_sql_model.to_domain()

    def update_last_login(self, admin_id: int) -> None:
        """Update the last_login_at timestamp for an admin user."""
        with self._get_session() as session:
            statement = select(AdminUserSQLModel).where(AdminUserSQLModel.id == admin_id)
            admin = session.exec(statement).first()
            if admin:
                admin.last_login_at = datetime.utcnow()
                admin.updated_at = datetime.utcnow()
                session.add(admin)
                session.commit()
            