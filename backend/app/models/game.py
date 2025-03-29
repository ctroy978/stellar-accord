# File: app/models/game.py
import uuid
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class Game(Base):
    __tablename__ = 'games'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    status = Column(String(50), default='setup', nullable=False)
    current_round = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=func.now())
    modified_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Add relationships
    phases = relationship("GamePhase", back_populates="game", cascade="all, delete-orphan")
    civilizations = relationship("Civilization", back_populates="game", cascade="all, delete-orphan")
    resources = relationship("Resource", back_populates="game", cascade="all, delete-orphan")
    projects = relationship("ProjectDevelopment", back_populates="game", cascade="all, delete-orphan")
    team_roles = relationship("TeamRole", back_populates="game", cascade="all, delete-orphan")
    accesses = relationship("GameAccess", back_populates="game", cascade="all, delete-orphan")