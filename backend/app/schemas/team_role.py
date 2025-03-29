# File: app/schemas/team_role.py
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from app.schemas.enums import TeamRoleName

# Base TeamRole schema
class TeamRoleBase(BaseModel):
    role: TeamRoleName

# Schema for creating a new TeamRole
class TeamRoleCreate(TeamRoleBase):
    game_id: UUID
    civilization_id: UUID
    player_id: UUID

# Schema for updating a TeamRole
class TeamRoleUpdate(TeamRoleBase):
    pass

# Schema for returning a TeamRole
class TeamRole(TeamRoleBase):
    id: UUID
    game_id: UUID
    civilization_id: UUID
    player_id: UUID
    assigned_at: datetime

    class Config:
        from_attributes = True
