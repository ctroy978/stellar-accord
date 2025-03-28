# File: app/crud/game.py

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.models.game import Game
from app.models.game_phase import GamePhase as GamePhaseModel
from app.schemas.game import GameCreate, GameUpdate
from app.schemas.enums import GameStatus, GamePhase

def get_game(db: Session, game_id: UUID) -> Optional[Game]:
    """Get a specific game by ID."""
    return db.query(Game).filter(Game.id == game_id).first()

def get_games(db: Session, skip: int = 0, limit: int = 100) -> List[Game]:
    """Get all games with pagination."""
    return db.query(Game).offset(skip).limit(limit).all()

def get_teacher_games(db: Session, teacher_id: UUID) -> List[Game]:
    """Get all games associated with a specific teacher."""
    return db.query(Game).join(
        models.GameAccess, Game.id == models.GameAccess.game_id
    ).filter(
        models.GameAccess.teacher_id == teacher_id
    ).all()

def create_game(db: Session, game: GameCreate) -> Game:
    """Create a new game and initialize its first phase."""
    db_game = Game(
        name=game.name,
        status=GameStatus.SETUP,
        current_round=1
    )
    
    db.add(db_game)
    
    try:
        db.commit()
        db.refresh(db_game)
        
        # Initialize the first phase (Planning phase of round 1)
        initial_phase = GamePhaseModel(
            game_id=db_game.id,
            round_number=1,
            phase=GamePhase.PLANNING,
            is_active=True,
            duration=game.phase_duration if hasattr(game, 'phase_duration') else None
        )
        
        db.add(initial_phase)
        db.commit()
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create game due to database constraint violation"
        )
    
    return db_game

def update_game(db: Session, game_id: UUID, game: GameUpdate) -> Game:
    """Update a game's details."""
    db_game = get_game(db, game_id=game_id)
    if not db_game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    # Update attributes if provided
    update_data = game.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_game, key, value)
    
    try:
        db.commit()
        db.refresh(db_game)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not update game due to database constraint violation"
        )
    
    return db_game

def delete_game(db: Session, game_id: UUID) -> None:
    """Delete a game and all associated data."""
    db_game = get_game(db, game_id=game_id)
    if not db_game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    db.delete(db_game)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not delete game due to database constraint violation"
        )

def advance_game_round(db: Session, game_id: UUID) -> Game:
    """Advance the game to the next round and initialize the planning phase."""
    db_game = get_game(db, game_id=game_id)
    if not db_game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    if db_game.status != GameStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot advance round for game in {db_game.status} status"
        )
    
    # Mark all active phases as inactive
    active_phases = db.query(GamePhaseModel).filter(
        GamePhaseModel.game_id == game_id,
        GamePhaseModel.is_active == True
    ).all()
    
    for phase in active_phases:
        phase.is_active = False
        phase.ended_at = datetime.now()
    
    # Increment the round
    db_game.current_round += 1
    
    # Create new planning phase for the new round
    new_phase = GamePhaseModel(
        game_id=game_id,
        round_number=db_game.current_round,
        phase=GamePhase.PLANNING,
        is_active=True,
        started_at=datetime.now()
    )
    
    db.add(new_phase)
    
    try:
        db.commit()
        db.refresh(db_game)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not advance game round due to database constraint violation"
        )
    
    return db_game

def update_game_status(db: Session, game_id: UUID, status: GameStatus) -> Game:
    """Update the game status with validation of status transitions."""
    db_game = get_game(db, game_id=game_id)
    if not db_game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    # Validate status transitions
    valid_transitions = {
        GameStatus.SETUP: [GameStatus.ACTIVE, GameStatus.PAUSED],
        GameStatus.ACTIVE: [GameStatus.PAUSED, GameStatus.COMPLETED],
        GameStatus.PAUSED: [GameStatus.ACTIVE, GameStatus.COMPLETED],
        GameStatus.COMPLETED: []  # No valid transitions from COMPLETED
    }
    
    if status not in valid_transitions[db_game.status]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status transition from {db_game.status} to {status}"
        )
    
    db_game.status = status
    
    try:
        db.commit()
        db.refresh(db_game)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not update game status due to database constraint violation"
        )
    
    return db_game