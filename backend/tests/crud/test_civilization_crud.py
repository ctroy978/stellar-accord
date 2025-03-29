# File: tests/crud/test_civilization_crud.py
import pytest
import uuid
from fastapi import HTTPException

from app.crud import civilization as crud_civilization
from app.models.civilization import Civilization
from app.schemas.civilization import CivilizationCreate, CivilizationUpdate
from app.schemas.enums import CivilizationName

class TestCivilizationCRUD:
    """Tests for Civilization CRUD operations."""
    
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
        # Create civilization data
        civ_data = CivilizationCreate(
            game_id=game_id,
            name=CivilizationName.THRIZOTH,
            display_name="The Thrizoth Empire",
            description="Plant-like beings with distributed consciousness",
            homeworld="Verdant",
            system_code="CD",
            communication_restrictions=["Vasku"]
        )
        
        # Create the civilization
        civ = crud_civilization.create_civilization(db_session, civilization=civ_data)
        
        # Verify the civilization was created
        assert civ.id is not None
        assert civ.game_id == game_id
        assert civ.name == CivilizationName.THRIZOTH
        assert civ.display_name == "The Thrizoth Empire"
        assert civ.description == "Plant-like beings with distributed consciousness"
        assert civ.homeworld == "Verdant"
        assert civ.system_code == "CD"
        assert civ.communication_restrictions == ["Vasku"]
    
    def test_create_invalid_civilization_name(self, db_session, game_id):
        """Test that creating a civilization with an invalid name raises an error."""
        # Create civilization data with an invalid name
        civ_data = CivilizationCreate(
            game_id=game_id,
            name="Invalid Civilization",  # Not in CivilizationName enum
            display_name="Invalid Civilization"
        )
        
        # Try to create the civilization
        with pytest.raises(HTTPException) as excinfo:
            crud_civilization.create_civilization(db_session, civilization=civ_data)
        
        # Verify the error
        assert excinfo.value.status_code == 400
        assert "Invalid civilization name" in excinfo.value.detail
    
    def test_create_duplicate_civilization(self, db_session, game_id):
        """Test that creating a duplicate civilization raises an error."""
        # Create civilization data
        civ_data = CivilizationCreate(
            game_id=game_id,
            name=CivilizationName.METHANE_COLLECTIVE,
            display_name="The Methane Collective"
        )
        
        # Create the civilization
        crud_civilization.create_civilization(db_session, civilization=civ_data)
        
        # Try to create another civilization with the same name
        with pytest.raises(HTTPException) as excinfo:
            crud_civilization.create_civilization(db_session, civilization=civ_data)
        
        # Verify the error
        assert excinfo.value.status_code == 400
        assert "already exists in this game" in excinfo.value.detail

    
    def test_create_too_many_civilizations(self, db_session, game_id):
        """Test that creating more than 6 civilizations raises an error."""
        # Create 6 civilizations
        civilization_names = [
            CivilizationName.THRIZOTH,
            CivilizationName.METHANE_COLLECTIVE,
            CivilizationName.SILICON_LIBERATION,
            CivilizationName.GLACIAN_CURRENT,
            CivilizationName.KYRATHI,
            CivilizationName.VASKU
        ]
        
        for name in civilization_names:
            civ_data = CivilizationCreate(
                game_id=game_id,
                name=name,
                display_name=f"The {name}"
            )
            
            crud_civilization.create_civilization(db_session, civilization=civ_data)
        
        # Try to create a 7th civilization by reusing an enum value
        # We'll create a fake enum value for this test
        with pytest.raises(HTTPException) as excinfo:
            # Try to create a new civilization with a different name
            # We have to mock this since we've used all the real enum values
            from unittest.mock import patch
            
            # Patch the validation function to bypass the enum check
            with patch('app.crud.civilization.CivilizationName') as mock_enum:
                mock_enum.return_value = "ExtraCivilization"
                
                civ_data = CivilizationCreate(
                    game_id=game_id,
                    name="ExtraCivilization",  # This would normally fail enum validation
                    display_name="The Extra Civilization"
                )
                
                crud_civilization.create_civilization(db_session, civilization=civ_data)
        
        # Verify the error
        assert excinfo.value.status_code == 400
        assert "Maximum of 6 civilizations" in excinfo.value.detail
    
    def test_get_civilization(self, db_session, game_id):
        """Test getting a civilization by ID."""
        # Create civilization data
        civ_data = CivilizationCreate(
            game_id=game_id,
            name=CivilizationName.SILICON_LIBERATION,
            display_name="The Silicon Liberation"
        )
        
        # Create the civilization
        created_civ = crud_civilization.create_civilization(db_session, civilization=civ_data)
        
        # Get the civilization
        retrieved_civ = crud_civilization.get_civilization(db_session, civilization_id=created_civ.id)
        
        # Verify the civilization was retrieved
        assert retrieved_civ is not None
        assert retrieved_civ.id == created_civ.id
        assert retrieved_civ.name == CivilizationName.SILICON_LIBERATION
    
    def test_get_civilizations_by_game(self, db_session, game_id):
        """Test getting all civilizations for a specific game."""
        # Create two civilizations
        civ1_data = CivilizationCreate(
            game_id=game_id,
            name=CivilizationName.GLACIAN_CURRENT,
            display_name="The Glacian Current"
        )
        
        civ2_data = CivilizationCreate(
            game_id=game_id,
            name=CivilizationName.KYRATHI,
            display_name="The Kyrathi"
        )
        
        # Create the civilizations
        crud_civilization.create_civilization(db_session, civilization=civ1_data)
        crud_civilization.create_civilization(db_session, civilization=civ2_data)
        
        # Get the civilizations for the game
        civilizations = crud_civilization.get_civilizations_by_game(db_session, game_id=game_id)
        
        # Verify the civilizations were retrieved
        assert len(civilizations) == 2
        assert civilizations[0].game_id == game_id
        assert civilizations[1].game_id == game_id
        
        # Verify the civilization names
        civ_names = [civ.name for civ in civilizations]
        assert CivilizationName.GLACIAN_CURRENT in civ_names
        assert CivilizationName.KYRATHI in civ_names
    
    def test_update_civilization(self, db_session, game_id):
        """Test updating a civilization."""
        # Create civilization data
        civ_data = CivilizationCreate(
            game_id=game_id,
            name=CivilizationName.VASKU,
            display_name="The Vasku",
            description="Energy-matter fluctuation beings"
        )
        
        # Create the civilization
        created_civ = crud_civilization.create_civilization(db_session, civilization=civ_data)
        
        # Update data
        update_data = CivilizationUpdate(
            display_name="The Mighty Vasku",
            description="Advanced energy-matter fluctuation beings",
            communication_restrictions=["Thrizoth"]
        )
        
        # Update the civilization
        updated_civ = crud_civilization.update_civilization(
            db_session,
            civilization_id=created_civ.id,
            civilization=update_data
        )
        
        # Verify the civilization was updated
        assert updated_civ.display_name == "The Mighty Vasku"
        assert updated_civ.description == "Advanced energy-matter fluctuation beings"
        assert updated_civ.communication_restrictions == ["Thrizoth"]
        assert updated_civ.name == CivilizationName.VASKU  # Unchanged field
    
    def test_delete_civilization(self, db_session, game_id):
        """Test deleting a civilization."""
        # Create civilization data
        civ_data = CivilizationCreate(
            game_id=game_id,
            name=CivilizationName.METHANE_COLLECTIVE,
            display_name="The Methane Collective"
        )
        
        # Create the civilization
        created_civ = crud_civilization.create_civilization(db_session, civilization=civ_data)
        
        # Delete the civilization
        crud_civilization.delete_civilization(db_session, civilization_id=created_civ.id)
        
        # Verify the civilization was deleted
        deleted_civ = crud_civilization.get_civilization(db_session, civilization_id=created_civ.id)
        assert deleted_civ is None
    
    def test_can_civilizations_communicate(self, db_session, game_id):
        """Test checking if two civilizations can communicate with each other."""
        # Create two civilizations with no communication restrictions
        civ1_data = CivilizationCreate(
            game_id=game_id,
            name=CivilizationName.SILICON_LIBERATION,
            display_name="The Silicon Liberation"
        )
        
        civ2_data = CivilizationCreate(
            game_id=game_id,
            name=CivilizationName.GLACIAN_CURRENT,
            display_name="The Glacian Current"
        )
        
        civ1 = crud_civilization.create_civilization(db_session, civilization=civ1_data)
        civ2 = crud_civilization.create_civilization(db_session, civilization=civ2_data)
        
        # Check if they can communicate
        can_communicate = crud_civilization.can_civilizations_communicate(
            db_session,
            civ1_id=civ1.id,
            civ2_id=civ2.id
        )
        
        # They should be able to communicate
        assert can_communicate is True
        
        # Create a civilization with communication restrictions
        civ3_data = CivilizationCreate(
            game_id=game_id,
            name=CivilizationName.THRIZOTH,
            display_name="The Thrizoth",
            communication_restrictions=["Vasku"]
        )
        
        civ4_data = CivilizationCreate(
            game_id=game_id,
            name=CivilizationName.VASKU,
            display_name="The Vasku",
            communication_restrictions=["Thrizoth"]
        )
        
        civ3 = crud_civilization.create_civilization(db_session, civilization=civ3_data)
        civ4 = crud_civilization.create_civilization(db_session, civilization=civ4_data)
        
        # Check if they can communicate
        can_communicate = crud_civilization.can_civilizations_communicate(
            db_session,
            civ1_id=civ3.id,
            civ2_id=civ4.id
        )
        
        # They should not be able to communicate
        assert can_communicate is False