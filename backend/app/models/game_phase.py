# File: app/models/game_phase.py
import uuid
from sqlalchemy import Column, String, ForeignKey, Integer, DateTime, Interval
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.base import Base

class GamePhase(Base):
    __tablename__ = 'game_phases'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    game_id = Column(UUID(as_uuid=True), ForeignKey('games.id', ondelete='CASCADE'), nullable=False)
    round_number = Column(Integer, default=1, nullable=False)
    phase = Column(String(50), nullable=False)  # Planning, Negotiation, Action, Resolution, Assessment
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    duration = Column(Interval, nullable=True)  # Scheduled duration of this phase
    is_active = Column(Boolean, default=False, nullable=False)
    
    # Composite unique constraint for active phase tracking
    __table_args__ = (
        UniqueConstraint('game_id', 'round_number', 'phase', name='uix_game_round_phase'),
    )