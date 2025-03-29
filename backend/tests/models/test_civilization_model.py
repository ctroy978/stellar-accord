# File: tests/models/test_civilization_model.py
import pytest
import uuid
from sqlalchemy.exc import IntegrityError

from app.models.civilization import Civilization
from app.schemas.enums import CivilizationName

class TestCivilizationModel:
    """Tests for the Civilization model."""
    
    @pytest.fixture
    def game_id(self, db_session):
        """Create a game and return its ID for testing."""
        from app.models.game import Game
        from app.schemas.enums import GameStatus
        
        # Create a game in the database
        game = Game(
            name="Test Game",
            status=GameStatus.SETUP,
            current_round=1
        )
        db_session.add(game)
        db_session.commit()
        db_session.refresh(game)
        return game.id
    
    def test_create_civilization(self, db_session, game_id):
        """Test creating a civilization."""
        # Create a civilization
        civ = Civilization(
            game_id=game_id,
            name=CivilizationName.THRIZOTH,
            display_name="The Thrizoth Empire",
            description="Plant-like beings with distributed consciousness",
            homeworld="Verdant",
            system_code="CD",
            communication_restrictions=["Vasku"]
        )
        
        db_session.add(civ)
        db_session.commit()
        db_session.refresh(civ)
        
        # Verify the civilization was created
        assert civ.id is not None
        assert civ.game_id == game_id
        assert civ.name == CivilizationName.THRIZOTH
        assert civ.display_name == "The Thrizoth Empire"
        assert civ.description == "Plant-like beings with distributed consciousness"
        assert civ.homeworld == "Verdant"
        assert civ.system_code == "CD"
        assert civ.communication_restrictions == ["Vasku"]
    
    def test_unique_civilization_per_game(self, db_session, game_id):
        """Test that a civilization name must be unique per game."""
        # Create a civilization
        civ1 = Civilization(
            game_id=game_id,
            name=CivilizationName.METHANE_COLLECTIVE,
            display_name="The Methane Collective"
        )
        
        db_session.add(civ1)
        db_session.commit()
        
        # Try to create another civilization with the same name in the same game
        civ2 = Civilization(
            game_id=game_id,
            name=CivilizationName.METHANE_COLLECTIVE,
            display_name="Another Methane Collective"
        )
        
        db_session.add(civ2)
        
        # This should raise an integrity error due to the unique constraint
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_same_civilization_different_games(self, db_session, game_id):
        """Test that the same civilization name can be used in different games."""
        # Create a civilization in one game
        civ1 = Civilization(
            game_id=game_id,
            name=CivilizationName.SILICON_LIBERATION,
            display_name="The Silicon Liberation"
        )
        
        db_session.add(civ1)
        db_session.commit()
        
        # Create another game in the database for the second civilization
        from app.models.game import Game
        from app.schemas.enums import GameStatus
        
        second_game = Game(
            name="Second Test Game",
            status=GameStatus.SETUP,
            current_round=1
        )
        db_session.add(second_game)
        db_session.commit()
        db_session.refresh(second_game)
        
        # Create another civilization with the same name in a different game
        civ2 = Civilization(
            game_id=second_game.id,  # Use the second game's ID
            name=CivilizationName.SILICON_LIBERATION,
            display_name="Another Silicon Liberation"
        )
        
        db_session.add(civ2)
        
        # This should succeed
        db_session.commit()
        db_session.refresh(civ2)
        
        # Verify the second civilization was created
        assert civ2.id is not None
        assert civ2.name == CivilizationName.SILICON_LIBERATION
        
        def test_update_civilization(self, db_session, game_id):
            """Test updating a civilization."""
            # Create a civilization
            civ = Civilization(
                game_id=game_id,
                name=CivilizationName.GLACIAN_CURRENT,
                display_name="The Glacian Current",
                description="Aquatic beings evolved under ice sheets"
            )
            
            db_session.add(civ)
            db_session.commit()
            
            # Update the civilization
            civ.display_name = "The Mighty Glacian Current"
            civ.description = "Advanced aquatic beings evolved under ice sheets"
            civ.communication_restrictions = ["Methane Collective"]
            
            db_session.commit()
            db_session.refresh(civ)
            
            # Verify the civilization was updated
            assert civ.display_name == "The Mighty Glacian Current"
            assert civ.description == "Advanced aquatic beings evolved under ice sheets"
            assert civ.communication_restrictions == ["Methane Collective"]
    
    def test_delete_civilization(self, db_session, game_id):
        """Test deleting a civilization."""
        # Create a civilization
        civ = Civilization(
            game_id=game_id,
            name=CivilizationName.KYRATHI,
            display_name="The Kyrathi"
        )
        
        db_session.add(civ)
        db_session.commit()
        
        # Store the civilization ID
        civ_id = civ.id
        
        # Delete the civilization
        db_session.delete(civ)
        db_session.commit()
        
        # Verify the civilization was deleted
        deleted_civ = db_session.query(Civilization).filter(Civilization.id == civ_id).first()
        assert deleted_civ is None