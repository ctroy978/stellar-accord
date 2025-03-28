# File: app/schemas/game_access.py
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from app.schemas.enums import AccessLevel

# Base GameAccess schema
class GameAccessBase(BaseModel):
    access_level: AccessLevel = AccessLevel.OWNER

# Schema for creating a new GameAccess
class GameAccessCreate(GameAccessBase):
    game_id: UUID
    teacher_id: UUID

# Schema for updating a GameAccess
class GameAccessUpdate(BaseModel):
    access_level: AccessLevel

# Schema for returning a GameAccess
class GameAccess(GameAccessBase):
    id: UUID
    game_id: UUID
    teacher_id: UUID
    created_at: datetime

    class Config:
        orm_mode = True