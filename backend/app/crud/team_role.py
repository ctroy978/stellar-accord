# File: app/crud/team_role.py

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import List, Optional
from uuid import UUID

from app.models.team_role import TeamRole
from app.schemas.team_role import TeamRoleCreate, TeamRoleUpdate
from app.schemas.enums import TeamRoleName

def get_team_role(db: Session, team_role_id: UUID) -> Optional[TeamRole]:
    """Get a specific team role by ID."""
    return db.query(TeamRole).filter(TeamRole.id == team_role_id).first()

def get_player_role(db: Session, game_id: UUID, civilization_id: UUID, player_id: UUID) -> Optional[TeamRole]:
    """Get a player's role within a specific civilization and game."""
    return db.query(TeamRole).filter(
        TeamRole.game_id == game_id,
        TeamRole.civilization_id == civilization_id,
        TeamRole.player_id == player_id
    ).first()

def get_civilization_roles(db: Session, game_id: UUID, civilization_id: UUID) -> List[TeamRole]:
    """Get all assigned roles for a specific civilization in a game."""
    return db.query(TeamRole).filter(
        TeamRole.game_id == game_id,
        TeamRole.civilization_id == civilization_id
    ).all()

def assign_role(db: Session, team_role: TeamRoleCreate) -> TeamRole:
    """Assign a role to a player within a civilization."""
    # Validate role against enum
    try:
        TeamRoleName(team_role.role)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid team role: {team_role.role}"
        )
    
    # Check if player is already assigned to a different civilization in this game
    existing_player_roles = db.query(TeamRole).filter(
        TeamRole.game_id == team_role.game_id,
        TeamRole.player_id == team_role.player_id,
        TeamRole.civilization_id != team_role.civilization_id
    ).all()
    
    if existing_player_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Player is already assigned to a different civilization in this game"
        )
    
    # Check if this role is already assigned in this civilization
    existing_civ_roles = get_civilization_roles(
        db, game_id=team_role.game_id, civilization_id=team_role.civilization_id
    )
    
    for role in existing_civ_roles:
        if role.role == team_role.role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role {team_role.role} is already assigned in this civilization"
            )
    
    db_team_role = TeamRole(
        game_id=team_role.game_id,
        civilization_id=team_role.civilization_id,
        player_id=team_role.player_id,
        role=team_role.role
    )
    
    db.add(db_team_role)
    
    try:
        db.commit()
        db.refresh(db_team_role)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not assign role due to database constraint violation"
        )
    
    return db_team_role

def update_team_role(db: Session, team_role_id: UUID, team_role: TeamRoleUpdate) -> TeamRole:
    """Update a team role assignment."""
    db_team_role = get_team_role(db, team_role_id=team_role_id)
    if not db_team_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team role not found"
        )
    
    # Validate new role against enum
    try:
        TeamRoleName(team_role.role)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid team role: {team_role.role}"
        )
    
    # Check if the new role is already assigned in this civilization
    if team_role.role != db_team_role.role:
        existing_roles = db.query(TeamRole).filter(
            TeamRole.game_id == db_team_role.game_id,
            TeamRole.civilization_id == db_team_role.civilization_id,
            TeamRole.role == team_role.role
        ).first()
        
        if existing_roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role {team_role.role} is already assigned in this civilization"
            )
    
    db_team_role.role = team_role.role
    
    try:
        db.commit()
        db.refresh(db_team_role)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not update team role due to database constraint violation"
        )
    
    return db_team_role

def remove_team_role(db: Session, team_role_id: UUID) -> None:
    """Remove a team role assignment."""
    db_team_role = get_team_role(db, team_role_id=team_role_id)
    if not db_team_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team role not found"
        )
    
    db.delete(db_team_role)
    # File: app/crud/team_role.py (continued)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not remove team role due to database constraint violation"
        )