# File: app/schemas/game_phase.py
from typing import Optional
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime, timedelta
from app.schemas.enums import GamePhase as GamePhaseEnum

# Base GamePhase schema
class GamePhaseBase(BaseModel):
    round_number: int
    phase: GamePhaseEnum
    duration: Optional[timedelta] = None

# Schema for creating a new GamePhase
class GamePhaseCreate(GamePhaseBase):
    game_id: UUID
    is_active: bool = False

# Schema for updating a GamePhase
class GamePhaseUpdate(BaseModel):
    is_active: Optional[bool] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration: Optional[timedelta] = None

# Schema for returning a GamePhase
class GamePhase(GamePhaseBase):
    id: UUID
    game_id: UUID
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    is_active: bool

    class Config:
        from_attributes = True
