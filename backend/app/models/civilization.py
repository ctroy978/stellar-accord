# File: app/models/civilization.py
import uuid
from sqlalchemy import Column, String, ForeignKey, Boolean, ARRAY, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class Civilization(Base):
    __tablename__ = 'civilizations'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    game_id = Column(UUID(as_uuid=True), ForeignKey('games.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(50), nullable=False)
    display_name = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    homeworld = Column(String(255), nullable=True)
    system_code = Column(String(10), nullable=True)
    communication_restrictions = Column(ARRAY(String), default=[])
    
    # Add relationship back-reference to Game
    game = relationship("Game", back_populates="civilizations")
    
    # Add relationship to TeamRole
    team_roles = relationship("TeamRole", back_populates="civilization", cascade="all, delete-orphan")
    
    # Composite unique constraint for one civilization per name per game
    __table_args__ = (
        UniqueConstraint('game_id', 'name', name='uix_civilization_game_name'),
    )