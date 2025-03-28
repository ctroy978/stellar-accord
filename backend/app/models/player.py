# File: app/models/player.py
import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.base import Base

class Player(Base):
    __tablename__ = 'players'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(255), nullable=False)
    display_name = Column(String(255), nullable=True)
    access_code = Column(String(20), nullable=False)  # Code used for joining/rejoining the game
    created_at = Column(DateTime, default=func.now())
    last_login = Column(DateTime, nullable=True)
    
    # Each access code is unique
    __table_args__ = (
        UniqueConstraint('access_code', name='uix_player_access_code'),
    )