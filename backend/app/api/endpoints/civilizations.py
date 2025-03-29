# File: app/api/endpoints/civilizations.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.schemas.civilization import Civilization, CivilizationCreate, CivilizationUpdate
from app.crud import civilization as crud_civilization

router = APIRouter()

@router.post("/", response_model=Civilization, status_code=status.HTTP_201_CREATED)
def create_civilization(civilization: CivilizationCreate, db: Session = Depends(get_db)):
    """Create a new civilization."""
    return crud_civilization.create_civilization(db, civilization=civilization)

@router.get("/game/{game_id}", response_model=List[Civilization])
def get_civilizations_by_game(game_id: UUID, db: Session = Depends(get_db)):
    """Get all civilizations for a specific game."""
    return crud_civilization.get_civilizations_by_game(db, game_id=game_id)

@router.get("/{civilization_id}", response_model=Civilization)
def get_civilization(civilization_id: UUID, db: Session = Depends(get_db)):
    """Get a specific civilization by ID."""
    db_civilization = crud_civilization.get_civilization(db, civilization_id=civilization_id)
    if db_civilization is None:
        raise HTTPException(status_code=404, detail="Civilization not found")
    return db_civilization

@router.patch("/{civilization_id}", response_model=Civilization)
def update_civilization(civilization_id: UUID, civilization: CivilizationUpdate, db: Session = Depends(get_db)):
    """Update a civilization."""
    return crud_civilization.update_civilization(db, civilization_id=civilization_id, civilization=civilization)

@router.delete("/{civilization_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_civilization(civilization_id: UUID, db: Session = Depends(get_db)):
    """Delete a civilization."""
    crud_civilization.delete_civilization(db, civilization_id=civilization_id)
    return None