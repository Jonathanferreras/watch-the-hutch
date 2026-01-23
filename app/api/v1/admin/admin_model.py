from enum import Enum
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class AdminRole(str, Enum):
    VIEWER = "VIEWER"
    EDITOR = "EDITOR"
    ADMIN = "ADMIN"

class AdminUser(BaseModel):
    id: int
    username: str
    role: AdminRole
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None
    is_active: bool = True

    class Config:
        from_attributes = True

class AdminCreate(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=8, max_length=128)
    role: AdminRole = AdminRole.VIEWER

class AdminLogin(BaseModel):
    username: str
    password: str
    