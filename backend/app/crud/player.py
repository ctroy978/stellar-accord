# File: app/crud/player.py

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import List, Optional
from uuid import UUID
import random
import string
from datetime import datetime

from app.models.player import Player
from app.models.team_role import TeamRole
from app.schemas.player import PlayerCreate, PlayerUpdate

def generate_access_code(length=8):
    """Generate a random alphanumeric access code."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def get_player(db: Session, player_id: UUID) -> Optional[Player]:
    """Get a specific player by ID."""
    return db.query(Player).filter(Player.id == player_id).first()

def get_player_by_access_code(db: Session, access_code: str) -> Optional[Player]:
    """Get a player by their access code."""
    return db.query(Player).filter(Player.access_code == access_code).first()

def get_players_by_game(db: Session, game_id: UUID) -> List[Player]:
    """Get all players participating in a specific game."""
    return db.query(Player).join(
        TeamRole, Player.id == TeamRole.player_id
    ).filter(
        TeamRole.game_id == game_id
    ).distinct().all()

def create_player(db: Session, player: PlayerCreate) -> Player:
    """Create a new player with a unique access code."""
    # Generate a unique access code
    access_code = player.access_code if player.access_code else generate_access_code()
    
    # Check if access code already exists
    while get_player_by_access_code(db, access_code):
        access_code = generate_access_code()
    
    db_player = Player(
        username=player.username,
        display_name=player.display_name,
        access_code=access_code
    )
    
    db.add(db_player)
    
    try:
        db.commit()
        db.refresh(db_player)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create player due to database constraint violation"
        )
    
    return db_player

def update_player(db: Session, player_id: UUID, player: PlayerUpdate) -> Player:
    """Update a player's details."""
    db_player = get_player(db, player_id=player_id)
    if not db_player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )
    
    # Update attributes if provided
    update_data = player.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_player, key, value)
    
    try:
        db.commit()
        db.refresh(db_player)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not update player due to database constraint violation"
        )
    
    return db_player

def delete_player(db: Session, player_id: UUID) -> None:
    """Delete a player."""
    db_player = get_player(db, player_id=player_id)
    if not db_player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )
    
    db.delete(db_player)
    
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not delete player due to database constraint violation"
        )

def update_last_login(db: Session, player_id: UUID) -> Player:
    """Update a player's last login timestamp."""
    db_player = get_player(db, player_id=player_id)
    if not db_player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )
    
    db_player.last_login = datetime.now()
    
    try:
        db.commit()
        db.refresh(db_player)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not update player last login due to database constraint violation"
        )
    
    return db_player