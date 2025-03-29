# File: app/schemas/game.py
from typing import Optional, List
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

from app.schemas.enums import GameStatus

# Base Game schema with common attributes
class GameBase(BaseModel):
    name: str
    status: GameStatus = GameStatus.SETUP

# Schema for creating a new Game
class GameCreate(GameBase):
    phase_duration: Optional[int] = None  # Optional duration in minutes for each phase

# Schema for updating a Game
class GameUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[GameStatus] = None
    current_round: Optional[int] = None

# Schema for returning a Game
class Game(GameBase):
    id: UUID
    current_round: int
    created_at: datetime
    modified_at: datetime

    class Config:
        from_attributes = True

# Schema for game statistics
class GameStats(BaseModel):
    total_civilizations: int
    total_players: int
    completed_rounds: int
    current_phase: str
    active_laws: List[str] = []
    
    class Config:
        from_attributes = True

# Schema for game with related data
class GameWithDetails(Game):
    stats: Optional[GameStats] = None
    
    class Config:
        from_attributes = True
