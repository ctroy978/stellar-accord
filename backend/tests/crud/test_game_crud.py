# File: tests/crud/test_game_crud.py
import pytest
from fastapi import HTTPException

from app.crud import game as crud_game
from app.models.game import Game
from app.models.game_phase import GamePhase as GamePhaseModel
from app.schemas.game import GameCreate, GameUpdate
from app.schemas.enums import GameStatus, GamePhase

class TestGameCRUD:
    """Tests for Game CRUD operations."""
    
    def test_create_game(self, db_session):
        """Test creating a game."""
        # Create game data
        game_data = GameCreate(
            name="New Test Game"
        )
        
        # Create the game
        game = crud_game.create_game(db_session, game=game_data)
        
        # Verify the game was created
        assert game.id is not None
        assert game.name == "New Test Game"
        assert game.status == GameStatus.SETUP
        assert game.current_round == 1
        
        # Verify the initial game phase was created
        phase = db_session.query(GamePhaseModel).filter(
            GamePhaseModel.game_id == game.id,
            GamePhaseModel.round_number == 1,
            GamePhaseModel.phase == GamePhase.PLANNING,
            GamePhaseModel.is_active == True
        ).first()
        
        assert phase is not None
    
    def test_get_game(self, db_session):
        """Test getting a game by ID."""
        # Create a game
        game_data = GameCreate(name="Game To Get")
        created_game = crud_game.create_game(db_session, game=game_data)
        
        # Get the game
        retrieved_game = crud_game.get_game(db_session, game_id=created_game.id)
        
        # Verify the game was retrieved
        assert retrieved_game is not None
        assert retrieved_game.id == created_game.id
        assert retrieved_game.name == "Game To Get"
    
    def test_update_game(self, db_session):
        """Test updating a game."""
        # Create a game
        game_data = GameCreate(name="Game To Update")
        created_game = crud_game.create_game(db_session, game=game_data)
        
        # Update the game
        update_data = GameUpdate(
            name="Updated Game Name",
            status=GameStatus.ACTIVE
        )
        
        updated_game = crud_game.update_game(
            db_session,
            game_id=created_game.id,
            game=update_data
        )
        
        # Verify the game was updated
        assert updated_game.name == "Updated Game Name"
        assert updated_game.status == GameStatus.ACTIVE
    
    def test_delete_game(self, db_session):
        """Test deleting a game."""
        # Create a game
        game_data = GameCreate(name="Game To Delete")
        created_game = crud_game.create_game(db_session, game=game_data)
        
        # Delete the game
        crud_game.delete_game(db_session, game_id=created_game.id)
        
        # Verify the game was deleted
        deleted_game = crud_game.get_game(db_session, game_id=created_game.id)
        assert deleted_game is None
    
    def test_update_game_status(self, db_session):
        """Test updating a game's status."""
        # Create a game
        game_data = GameCreate(name="Game Status Update")
        created_game = crud_game.create_game(db_session, game=game_data)
        
        # Update the game status to ACTIVE
        updated_game = crud_game.update_game_status(
            db_session,
            game_id=created_game.id,
            status=GameStatus.ACTIVE
        )
        
        # Verify the status was updated
        assert updated_game.status == GameStatus.ACTIVE
        
        # Update the status to PAUSED
        updated_game = crud_game.update_game_status(
            db_session,
            game_id=created_game.id,
            status=GameStatus.PAUSED
        )
        
        # Verify the status was updated
        assert updated_game.status == GameStatus.PAUSED
    
    def test_invalid_status_transition(self, db_session):
        """Test that invalid status transitions raise an error."""
        # Create a game
        game_data = GameCreate(name="Invalid Status Transition")
        created_game = crud_game.create_game(db_session, game=game_data)
        
        # Try to transition directly from SETUP to COMPLETED
        with pytest.raises(HTTPException) as excinfo:
            crud_game.update_game_status(
                db_session,
                game_id=created_game.id,
                status=GameStatus.COMPLETED
            )
        
        # Verify the error
        assert excinfo.value.status_code == 400
        assert "Invalid status transition" in excinfo.value.detail
    
    def test_advance_game_round(self, db_session):
        """Test advancing a game to the next round."""
        # Create a game
        game_data = GameCreate(name="Advance Round Test")
        created_game = crud_game.create_game(db_session, game=game_data)
        
        # Set the game to ACTIVE
        crud_game.update_game_status(
            db_session,
            game_id=created_game.id,
            status=GameStatus.ACTIVE
        )
        
        # Advance the round
        advanced_game = crud_game.advance_game_round(
            db_session,
            game_id=created_game.id
        )
        
        # Verify the round was advanced
        assert advanced_game.current_round == 2
        
        # Verify the new planning phase was created
        new_phase = db_session.query(GamePhaseModel).filter(
            GamePhaseModel.game_id == created_game.id,
            GamePhaseModel.round_number == 2,
            GamePhaseModel.phase == GamePhase.PLANNING,
            GamePhaseModel.is_active == True
        ).first()
        
        assert new_phase is not None
        
        # Verify the old phase is no longer active
        old_phase = db_session.query(GamePhaseModel).filter(
            GamePhaseModel.game_id == created_game.id,
            GamePhaseModel.round_number == 1,
            GamePhaseModel.is_active == True
        ).first()
        
        assert old_phase is None