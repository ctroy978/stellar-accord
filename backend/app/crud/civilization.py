# File: app/crud/civilization.py

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import List, Optional
from uuid import UUID

from app.models.civilization import Civilization
from app.schemas.civilization import CivilizationCreate, CivilizationUpdate
from app.schemas.enums import CivilizationName

def get_civilization(db: Session, civilization_id: UUID) -> Optional[Civilization]:
    """Get a specific civilization by ID."""
    return db.query(Civilization).filter(Civilization.id == civilization_id).first()

def get_civilizations_by_game(db: Session, game_id: UUID) -> List[Civilization]:
    """Get all civilizations for a specific game."""
    return db.query(Civilization).filter(Civilization.game_id == game_id).all()

def create_civilization(db: Session, civilization: CivilizationCreate) -> Civilization:
    """Create a new civilization with validation."""
    # Validate civilization name against enum
    try:
        CivilizationName(civilization.name)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid civilization name: {civilization.name}"
        )
    
    # Check if we already have 6 civilizations for this game
    existing_civs = get_civilizations_by_game(db, game_id=civilization.game_id)
    if len(existing_civs) >= 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum of 6 civilizations per game allowed"
        )
    
    # Check if this civilization name is already used in this game
    for civ in existing_civs:
        if civ.name == civilization.name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Civilization {civilization.name} already exists in this game"
            )
    
    db_civilization = Civilization(
        game_id=civilization.game_id,
        name=civilization.name,
        display_name=civilization.display_name,
        description=civilization.description,
        homeworld=civilization.homeworld,
        system_code=civilization.system_code,
        communication_restrictions=civilization.communication_restrictions
    )
    
    db.add(db_civilization)
    
    try:
        db.commit()
        db.refresh(db_civilization)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create civilization due to database constraint violation"
        )
    
    return db_civilization

def update_civilization(db: Session, civilization_id: UUID, civilization: CivilizationUpdate) -> Civilization:
    """Update a civilization's details."""
    db_civilization = get_civilization(db, civilization_id=civilization_id)
    if not db_civilization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Civilization not found"
        )
    
    # Update attributes if provided
    update_data = civilization.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_civilization, key, value)
    
    try:
        db.commit()
        db.refresh(db_civilization)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not update civilization due to database constraint violation"
        )
    
    return db_civilization

def delete_civilization(db: Session, civilization_id: UUID) -> None:
    """Delete a civilization."""
    db_civilization = get_civilization(db, civilization_id=civilization_id)
    if not db_civilization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Civilization not found"
        )
    
    db.delete(db_civilization)
    
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not delete civilization due to database constraint violation"
        )

def can_civilizations_communicate(db: Session, civ1_id: UUID, civ2_id: UUID) -> bool:
    """Check if two civilizations can communicate with each other."""
    civ1 = get_civilization(db, civilization_id=civ1_id)
    civ2 = get_civilization(db, civilization_id=civ2_id)
    
    if not civ1 or not civ2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or both civilizations not found"
        )
    
    # Check if either civilization has a communication restriction with the other
    return (
        civ2.name not in civ1.communication_restrictions and
        civ1.name not in civ2.communication_restrictions
    )