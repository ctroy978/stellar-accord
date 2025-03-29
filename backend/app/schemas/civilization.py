# File: app/schemas/civilization.py
from typing import List, Optional
from pydantic import BaseModel, Field
from uuid import UUID

# Base Civilization schema with common attributes
class CivilizationBase(BaseModel):
    name: str
    display_name: Optional[str] = None
    description: Optional[str] = None
    homeworld: Optional[str] = None
    system_code: Optional[str] = None
    communication_restrictions: Optional[List[str]] = Field(default_factory=list)

# Schema for creating a new Civilization
class CivilizationCreate(CivilizationBase):
    game_id: UUID

# Schema for updating a Civilization
class CivilizationUpdate(BaseModel):
    display_name: Optional[str] = None
    description: Optional[str] = None
    homeworld: Optional[str] = None
    system_code: Optional[str] = None
    communication_restrictions: Optional[List[str]] = None

# Schema for returning a Civilization
class Civilization(CivilizationBase):
    id: UUID
    game_id: UUID

    class Config:
        from_attributes = True
