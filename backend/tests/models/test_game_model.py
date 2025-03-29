# File: tests/models/test_game_model.py
import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from app.models.game import Game
from app.schemas.enums import GameStatus

class TestGameModel:
    """Tests for the Game model."""
    
    def test_create_game(self, db_session):
        """Test creating a game."""
        # Create a game
        game = Game(
            name="Test Game",
            status=GameStatus.SETUP,
            current_round=1
        )
        
        db_session.add(game)
        db_session.commit()
        db_session.refresh(game)
        
        # Verify the game was created
        assert game.id is not None
        assert game.name == "Test Game"
        assert game.status == GameStatus.SETUP
        assert game.current_round == 1
        assert isinstance(game.created_at, datetime)
        assert isinstance(game.modified_at, datetime)
    
    def test_update_game(self, db_session):
        """Test updating a game."""
        # Create a game
        game = Game(
            name="Game To Update",
            status=GameStatus.SETUP,
            current_round=1
        )
        
        db_session.add(game)
        db_session.commit()
        
        # Update the game
        game.name = "Updated Game Name"
        game.status = GameStatus.ACTIVE
        game.current_round = 2
        
        db_session.commit()
        db_session.refresh(game)
        
        # Verify the game was updated
        assert game.name == "Updated Game Name"
        assert game.status == GameStatus.ACTIVE
        assert game.current_round == 2
    
    def test_delete_game(self, db_session):
        """Test deleting a game."""
        # Create a game
        game = Game(
            name="Game To Delete",
            status=GameStatus.SETUP,
            current_round=1
        )
        
        db_session.add(game)
        db_session.commit()
        
        # Store the game ID
        game_id = game.id
        
        # Delete the game
        db_session.delete(game)
        db_session.commit()
        
        # Verify the game was deleted
        deleted_game = db_session.query(Game).filter(Game.id == game_id).first()
        assert deleted_game is None