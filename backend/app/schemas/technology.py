# file: app/schemas/technology.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Union
from uuid import UUID
from datetime import datetime

# BigTechComponent schemas
class BigTechComponentBase(BaseModel):
    name: str
    description: Optional[str] = None
    tech_group: Optional[str] = None

class BigTechComponentCreate(BigTechComponentBase):
    pass

class BigTechComponent(BigTechComponentBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

# UberTechComponent schemas
class UberTechComponentBase(BaseModel):
    name: str
    description: Optional[str] = None

class UberTechComponentCreate(UberTechComponentBase):
    pass

class UberTechComponent(UberTechComponentBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

# UniversalProject schemas
class UniversalProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    beneficiaries: List[str] = Field(default_factory=list)
    harmed: List[str] = Field(default_factory=list)

class UniversalProjectCreate(UniversalProjectBase):
    pass

class UniversalProject(UniversalProjectBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

# TechRequirement schemas
class TechRequirementBase(BaseModel):
    tech_type: str
    tech_id: UUID
    required_tech_type: str
    required_tech_id: UUID
    quantity: int = 1

class TechRequirementCreate(TechRequirementBase):
    pass

class TechRequirement(TechRequirementBase):
    id: UUID

    class Config:
        from_attributes = True

# ProjectDevelopment schemas
class ProjectDevelopmentBase(BaseModel):
    project_type: str
    project_id: UUID
    current_phase: str = "research"

class ProjectDevelopmentCreate(ProjectDevelopmentBase):
    game_id: UUID
    civilization_id: UUID

class ProjectDevelopment(ProjectDevelopmentBase):
    id: UUID
    game_id: UUID
    civilization_id: UUID
    progress_percentage: float
    started_at: datetime
    completed_at: Optional[datetime] = None
    is_sabotaged: bool = False
    sabotage_round: Optional[int] = None

    class Config:
        from_attributes = True

# TechnologyOwnership schemas
class TechnologyOwnershipBase(BaseModel):
    technology_type: str
    technology_id: UUID

class TechnologyOwnershipCreate(TechnologyOwnershipBase):
    game_id: UUID
    owner_id: UUID

class TechnologyOwnership(TechnologyOwnershipBase):
    id: UUID
    game_id: UUID
    owner_id: UUID
    acquired_at: datetime

    class Config:
        from_attributes = True

# ProjectComponentAssignment schemas
class ProjectComponentAssignmentBase(BaseModel):
    component_type: str
    component_id: UUID

class ProjectComponentAssignmentCreate(ProjectComponentAssignmentBase):
    game_id: UUID
    project_id: UUID

class ProjectComponentAssignment(ProjectComponentAssignmentBase):
    id: UUID
    game_id: UUID
    project_id: UUID
    assigned_at: datetime

    class Config:
        from_attributes = True
