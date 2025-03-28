# File: app/crud/game_phase.py

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.models.game_phase import GamePhase as GamePhaseModel
from app.models.game import Game
from app.schemas.game_phase import GamePhaseCreate, GamePhaseUpdate
from app.schemas.enums import GamePhase, GameStatus

def get_game_phase(db: Session, game_phase_id: UUID) -> Optional[GamePhaseModel]:
    """Get a specific game phase by ID."""
    return db.query(GamePhaseModel).filter(GamePhaseModel.id == game_phase_id).first()

def get_active_phase(db: Session, game_id: UUID) -> Optional[GamePhaseModel]:
    """Get the currently active phase for a game."""
    return db.query(GamePhaseModel).filter(
        GamePhaseModel.game_id == game_id,
        GamePhaseModel.is_active == True
    ).first()

def get_game_phases(db: Session, game_id: UUID) -> List[GamePhaseModel]:
    """Get all phases for a specific game."""
    return db.query(GamePhaseModel).filter(
        GamePhaseModel.game_id == game_id
    ).order_by(
        GamePhaseModel.round_number,
        # This ordering assumes phases are stored in order: Planning, Negotiation, Action, Resolution, Assessment
        GamePhaseModel.phase
    ).all()

def create_game_phase(db: Session, game_phase: GamePhaseCreate) -> GamePhaseModel:
    """Create a new game phase."""
    # Check if game exists
    game = db.query(Game).filter(Game.id == game_phase.game_id).first()
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    # If creating an active phase, ensure no other active phases exist
    if game_phase.is_active:
        active_phase = get_active_phase(db, game_id=game_phase.game_id)
        if active_phase:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Another phase is already active for this game"
            )
    
    db_game_phase = GamePhaseModel(
        game_id=game_phase.game_id,
        round_number=game_phase.round_number,
        phase=game_phase.phase,
        duration=game_phase.duration,
        is_active=game_phase.is_active,
        started_at=datetime.now() if game_phase.is_active else None
    )
    
    db.add(db_game_phase)
    
    try:
        db.commit()
        db.refresh(db_game_phase)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create game phase due to database constraint violation"
        )
    
    return db_game_phase

def start_phase(db: Session, game_phase_id: UUID) -> GamePhaseModel:
    """Start a game phase."""
    db_game_phase = get_game_phase(db, game_phase_id=game_phase_id)
    if not db_game_phase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game phase not found"
        )
    
    # Check if another phase is already active
    active_phase = get_active_phase(db, game_id=db_game_phase.game_id)
    if active_phase and active_phase.id != db_game_phase.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Another phase is already active for this game"
        )
    
    # If this phase is already active, just return it
    if db_game_phase.is_active:
        return db_game_phase
    
    db_game_phase.is_active = True
    db_game_phase.started_at = datetime.now()
    
    try:
        db.commit()
        db.refresh(db_game_phase)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not start game phase due to database constraint violation"
        )
    
    return db_game_phase

def end_phase(db: Session, game_phase_id: UUID) -> GamePhaseModel:
    """End an active game phase."""
    db_game_phase = get_game_phase(db, game_phase_id=game_phase_id)
    if not db_game_phase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game phase not found"
        )
    
    if not db_game_phase.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot end a phase that is not active"
        )
    
    db_game_phase.is_active = False
    db_game_phase.ended_at = datetime.now()
    
    try:
        db.commit()
        db.refresh(db_game_phase)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not end game phase due to database constraint violation"
        )
    
    return db_game_phase

def advance_to_next_phase(db: Session, game_id: UUID) -> GamePhaseModel:
    """
    Advance the game to the next phase in sequence.
    Sequence: Planning -> Negotiation -> Action -> Resolution -> Assessment -> (new round) Planning
    """
    # Check if game exists and is active
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    if game.status != GameStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot advance phase for game in {game.status} status"
        )
    
    # Get current active phase
    current_phase = get_active_phase(db, game_id=game_id)
    if not current_phase:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active phase found for this game"
        )
    
    # End current phase
    current_phase.is_active = False
    current_phase.ended_at = datetime.now()
    
    # Determine next phase
    phase_sequence = [
        GamePhase.PLANNING,
        GamePhase.NEGOTIATION,
        GamePhase.ACTION,
        GamePhase.RESOLUTION,
        GamePhase.ASSESSMENT
    ]
    
    current_phase_index = phase_sequence.index(current_phase.phase)
    next_round = current_phase.round_number
    
    if current_phase_index == len(phase_sequence) - 1:
        # If we're at Assessment, go to Planning of next round
        next_phase_name = GamePhase.PLANNING
        next_round += 1
        # Update the game's current round
        game.current_round = next_round
    else:
        # Otherwise go to the next phase in the sequence
        next_phase_name = phase_sequence[current_phase_index + 1]
    
    # Create new phase
    new_phase = GamePhaseModel(
        game_id=game_id,
        round_number=next_round,
        phase=next_phase_name,
        is_active=True,
        started_at=datetime.now(),
        duration=current_phase.duration  # Copy duration from previous phase
    )
    
    db.add(new_phase)
    
    try:
        db.commit()
        db.refresh(new_phase)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not advance to next phase due to database constraint violation"
        )
    
    return new_phase