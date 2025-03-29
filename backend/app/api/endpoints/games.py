# File: app/api/endpoints/games.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.db.session import get_db
from app.schemas.game import Game, GameCreate, GameUpdate, GameWithDetails
from app.crud import game as crud_game

router = APIRouter()

@router.post("/", response_model=Game, status_code=status.HTTP_201_CREATED)
def create_game(game: GameCreate, db: Session = Depends(get_db)):
    """Create a new game."""
    return crud_game.create_game(db, game=game)

@router.get("/", response_model=List[Game])
def get_games(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all games."""
    return crud_game.get_games(db, skip=skip, limit=limit)

@router.get("/{game_id}", response_model=Game)
def get_game(game_id: UUID, db: Session = Depends(get_db)):
    """Get a specific game by ID."""
    db_game = crud_game.get_game(db, game_id=game_id)
    if db_game is None:
        raise HTTPException(status_code=404, detail="Game not found")
    return db_game

@router.patch("/{game_id}", response_model=Game)
def update_game(game_id: UUID, game: GameUpdate, db: Session = Depends(get_db)):
    """Update a game."""
    return crud_game.update_game(db, game_id=game_id, game=game)

@router.delete("/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_game(game_id: UUID, db: Session = Depends(get_db)):
    """Delete a game."""
    crud_game.delete_game(db, game_id=game_id)
    return None