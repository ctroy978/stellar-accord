# File: app/models/team_role.py
import uuid
from sqlalchemy import Column, String, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class TeamRole(Base):
    __tablename__ = 'team_roles'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    game_id = Column(UUID(as_uuid=True), ForeignKey('games.id', ondelete='CASCADE'), nullable=False)
    civilization_id = Column(UUID(as_uuid=True), ForeignKey('civilizations.id', ondelete='CASCADE'), nullable=False)
    player_id = Column(UUID(as_uuid=True), ForeignKey('players.id', ondelete='CASCADE'), nullable=False)
    role = Column(String(50), nullable=False)
    assigned_at = Column(DateTime, default=func.now())
    
    # Add relationships
    game = relationship("Game", back_populates="team_roles")
    civilization = relationship("Civilization", back_populates="team_roles")
    player = relationship("Player", back_populates="team_roles")
    
    # Each player can have only one role per civilization per game
    __table_args__ = (
        UniqueConstraint('game_id', 'civilization_id', 'player_id', name='uix_player_role_per_civilization'),
    )