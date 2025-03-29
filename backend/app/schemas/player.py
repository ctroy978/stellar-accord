# File: app/schemas/player.py
from typing import Optional
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

# Base Player schema
class PlayerBase(BaseModel):
    username: str
    display_name: Optional[str] = None

# Schema for creating a new Player
class PlayerCreate(PlayerBase):
    access_code: str

# Schema for updating a Player
class PlayerUpdate(BaseModel):
    username: Optional[str] = None
    display_name: Optional[str] = None

# Schema for returning a Player
class Player(PlayerBase):
    id: UUID
    access_code: str
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True
