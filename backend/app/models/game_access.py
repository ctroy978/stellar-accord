# File: app/models/game_access.py
import uuid
from sqlalchemy import Column, ForeignKey, DateTime, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.base import Base

class GameAccess(Base):
    __tablename__ = 'game_access'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    game_id = Column(UUID(as_uuid=True), ForeignKey('games.id', ondelete='CASCADE'), nullable=False)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey('teachers.id', ondelete='CASCADE'), nullable=False)
    access_level = Column(String(50), default='owner', nullable=False)  # owner, viewer, etc.
    created_at = Column(DateTime, default=func.now())
    
    # Each teacher can have only one access record per game
    __table_args__ = (
        UniqueConstraint('game_id', 'teacher_id', name='uix_teacher_game_access'),
    )