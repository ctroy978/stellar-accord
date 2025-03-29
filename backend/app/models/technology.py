# file: app/models/technology.py
import uuid
from sqlalchemy import Column, String, ForeignKey, Integer, Float, Boolean, DateTime, Text, ARRAY, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class BigTechComponent(Base):
    __tablename__ = 'big_tech_components'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    tech_group = Column(String(50), nullable=True)  # Group identifier (A-F as per design doc)
    created_at = Column(DateTime, default=func.now())

class UberTechComponent(Base):
    __tablename__ = 'uber_tech_components'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())

class UniversalProject(Base):
    __tablename__ = 'universal_projects'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    beneficiaries = Column(ARRAY(String), default=[])  # Array of civilization IDs that benefit
    harmed = Column(ARRAY(String), default=[])  # Array of civilization IDs that are harmed
    created_at = Column(DateTime, default=func.now())

class TechRequirement(Base):
    __tablename__ = 'tech_requirements'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tech_type = Column(String(50), nullable=False)  # 'universal', 'uber', or 'big'
    tech_id = Column(UUID(as_uuid=True), nullable=False)
    required_tech_type = Column(String(50), nullable=False)  # 'uber', 'big', or 'resource'
    required_tech_id = Column(UUID(as_uuid=True), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)  # For resources

    # Ensure unique requirements
    __table_args__ = (
        UniqueConstraint('tech_type', 'tech_id', 'required_tech_type', 'required_tech_id', 
                         name='uix_tech_requirement'),
    )

class ProjectDevelopment(Base):
    __tablename__ = 'project_developments'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    game_id = Column(UUID(as_uuid=True), ForeignKey('games.id', ondelete='CASCADE'), nullable=False)
    civilization_id = Column(UUID(as_uuid=True), ForeignKey('civilizations.id', ondelete='CASCADE'), nullable=False)
    project_type = Column(String(50), nullable=False)
    project_id = Column(UUID(as_uuid=True), nullable=False)
    current_phase = Column(String(50), nullable=False)
    progress_percentage = Column(Float, default=0.0, nullable=False)
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime, nullable=True)
    is_sabotaged = Column(Boolean, default=False)
    sabotage_round = Column(Integer, nullable=True)
    
    # Add relationships
    game = relationship("Game", back_populates="projects")
    civilization = relationship("Civilization", foreign_keys=[civilization_id])
    component_assignments = relationship("ProjectComponentAssignment", back_populates="project", cascade="all, delete-orphan")
    
    # Ensure a civilization isn't building the same project twice
    __table_args__ = (
        UniqueConstraint('game_id', 'civilization_id', 'project_type', 'project_id', 
                         name='uix_civ_project'),
    )

class TechnologyOwnership(Base):
    __tablename__ = 'technology_ownership'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    game_id = Column(UUID(as_uuid=True), ForeignKey('games.id', ondelete='CASCADE'), nullable=False)
    owner_id = Column(UUID(as_uuid=True), nullable=False)
    technology_type = Column(String(50), nullable=False)  # 'universal', 'uber', or 'big'
    technology_id = Column(UUID(as_uuid=True), nullable=False)
    acquired_at = Column(DateTime, default=func.now())
    
    # Ensure a civilization doesn't own the same technology twice
    __table_args__ = (
        UniqueConstraint('game_id', 'owner_id', 'technology_type', 'technology_id', 
                         name='uix_tech_ownership'),
    )

class ProjectComponentAssignment(Base):
    __tablename__ = 'project_component_assignments'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    game_id = Column(UUID(as_uuid=True), ForeignKey('games.id', ondelete='CASCADE'), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey('project_developments.id', ondelete='CASCADE'), nullable=False)
    component_id = Column(UUID(as_uuid=True), nullable=False)
    component_type = Column(String(50), nullable=False)
    assigned_at = Column(DateTime, default=func.now())
    
    # Add relationship
    project = relationship("ProjectDevelopment", back_populates="component_assignments")
    game = relationship("Game")
    
    # Ensure a component can only be assigned to one project
    __table_args__ = (
        UniqueConstraint('game_id', 'component_id', 'component_type', name='uix_component_assignment'),
    )