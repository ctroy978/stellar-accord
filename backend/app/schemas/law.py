# File: app/schemas/law.py
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from uuid import UUID
from datetime import datetime

# Law Template Schemas
class LawTemplateInfo(BaseModel):
    template_id: str
    name: str
    description: str
    category: Optional[str] = None
    parameters: List[Dict[str, Any]]

class LawTemplateDetails(LawTemplateInfo):
    template_text: str
    example: str

# Law Proposal Schemas
class LawProposalCreate(BaseModel):
    template_id: str
    parameters: Dict[str, Any]
    proposing_civilization: str
    game_id: UUID

class LawProposal(BaseModel):
    id: UUID
    game_id: UUID
    template_id: str
    template_name: str
    parameters: Dict[str, Any]
    category: Optional[str] = None
    law_text: str
    effects: Dict[str, Any]
    proposing_civilization: str
    round_number: int
    votes: List[str] = Field(default_factory=list)
    created_at: datetime

    class Config:
        from_attributes = True

# Law Vote Schema
class LawVote(BaseModel):
    game_id: UUID
    proposal_id: UUID
    voting_civilization: str
    vote: bool  # True for yes, False for no/abstain

# Enacted Law Schema
class EnactedLaw(BaseModel):
    id: UUID
    game_id: UUID
    proposal_id: UUID
    law_text: str
    template_id: str
    parameters: Dict[str, Any]
    category: Optional[str] = None
    effects: Dict[str, Any]
    enacted_round: int
    duration: int  # Number of rounds the law is active
    is_active: bool
    voided_by: Optional[UUID] = None
    enacted_at: datetime

    class Config:
        from_attributes = True

# Law Resolution Schema
class LawResolution(BaseModel):
    resolution: str

class LawEffectsRequest(BaseModel):
    action_type: str
    context_data: Dict[str, Any] = Field(default_factory=dict)