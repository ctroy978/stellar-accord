# File: app/models/law.py
import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class LawProposal(Base):
    __tablename__ = 'law_proposals'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    game_id = Column(UUID(as_uuid=True), ForeignKey('games.id', ondelete='CASCADE'), nullable=False)
    template_id = Column(String(255), nullable=False)
    template_name = Column(String(255), nullable=False)
    parameters = Column(JSON, nullable=False)
    category = Column(String(50), nullable=True)
    law_text = Column(String, nullable=False)
    effects = Column(JSON, nullable=False)
    proposing_civilization = Column(String(255), nullable=False)
    round_number = Column(Integer, nullable=False)
    votes = Column(JSON, default=list, nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    game = relationship("Game")

class EnactedLaw(Base):
    __tablename__ = 'enacted_laws'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    game_id = Column(UUID(as_uuid=True), ForeignKey('games.id', ondelete='CASCADE'), nullable=False)
    proposal_id = Column(UUID(as_uuid=True), ForeignKey('law_proposals.id'), nullable=False)
    law_text = Column(String, nullable=False)
    template_id = Column(String(255), nullable=False)
    parameters = Column(JSON, nullable=False)
    category = Column(String(50), nullable=True)
    effects = Column(JSON, nullable=False)
    enacted_round = Column(Integer, nullable=False)
    duration = Column(Integer, default=3, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    voided_by = Column(UUID(as_uuid=True), nullable=True)
    enacted_at = Column(DateTime, default=func.now())
    
    # Relationships
    game = relationship("Game")
    proposal = relationship("LawProposal")