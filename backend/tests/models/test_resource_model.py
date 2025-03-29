# File: tests/models/test_resource_model.py
import pytest
import uuid
from sqlalchemy.exc import IntegrityError

from app.models.resource import ResourceType, Resource
from app.schemas.enums import ResourceCategory, ResourceRarity

class TestResourceTypeModel:
    """Tests for the ResourceType model."""
    
    def test_create_resource_type(self, db_session):
        """Test creating a resource type."""
        # Create a resource type
        resource_type = ResourceType(
            name="Test Resource",
            category=ResourceCategory.RAW_MATERIAL,
            rarity=ResourceRarity.COMMON,
            description="A test resource",
            producible_by=["Thrizoth", "Methane Collective"]
        )
        
        db_session.add(resource_type)
        db_session.commit()
        db_session.refresh(resource_type)
        
        # Verify the resource type was created
        assert resource_type.id is not None
        assert resource_type.name == "Test Resource"
        assert resource_type.category == ResourceCategory.RAW_MATERIAL
        assert resource_type.rarity == ResourceRarity.COMMON
        assert resource_type.description == "A test resource"
        assert resource_type.producible_by == ["Thrizoth", "Methane Collective"]
    
    def test_unique_resource_type_name(self, db_session):
        """Test that resource type names must be unique."""
        # Create a resource type
        resource_type1 = ResourceType(
            name="Unique Resource",
            category=ResourceCategory.RAW_MATERIAL,
            rarity=ResourceRarity.COMMON
        )
        
        db_session.add(resource_type1)
        db_session.commit()
        
        # Try to create another resource type with the same name
        resource_type2 = ResourceType(
            name="Unique Resource",
            category=ResourceCategory.TECHNOLOGY,
            rarity=ResourceRarity.RARE
        )
        
        db_session.add(resource_type2)
        
        # This should raise an integrity error due to the unique constraint
        with pytest.raises(IntegrityError):
            db_session.commit()

class TestResourceModel:
    """Tests for the Resource model."""
    
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


    
    @pytest.fixture
    def owner_id(self):
        """Generate an owner ID for testing."""
        return uuid.uuid4()
    
    @pytest.fixture
    def resource_type(self, db_session):
        """Create a resource type for testing."""
        resource_type = ResourceType(
            name="Resource For Inventory",
            category=ResourceCategory.RAW_MATERIAL,
            rarity=ResourceRarity.COMMON
        )
        
        db_session.add(resource_type)
        db_session.commit()
        db_session.refresh(resource_type)
        return resource_type
    
    def test_create_resource(self, db_session, game_id, owner_id, resource_type):
        """Test creating a resource."""
        # Create a resource
        resource = Resource(
            game_id=game_id,
            owner_id=owner_id,
            resource_type_id=resource_type.id,
            quantity=100
        )
        
        db_session.add(resource)
        db_session.commit()
        db_session.refresh(resource)
        
        # Verify the resource was created
        assert resource.id is not None
        assert resource.game_id == game_id
        assert resource.owner_id == owner_id
        assert resource.resource_type_id == resource_type.id
        assert resource.quantity == 100
    
    def test_unique_resource_constraint(self, db_session, game_id, owner_id, resource_type):
        """Test that resources must be unique per game, owner, and type."""
        # Create a resource
        resource1 = Resource(
            game_id=game_id,
            owner_id=owner_id,
            resource_type_id=resource_type.id,
            quantity=100
        )
        
        db_session.add(resource1)
        db_session.commit()
        
        # Try to create another resource with the same game, owner, and type
        resource2 = Resource(
            game_id=game_id,
            owner_id=owner_id,
            resource_type_id=resource_type.id,
            quantity=50
        )
        
        db_session.add(resource2)
        
        # This should raise an integrity error due to the unique constraint
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_update_resource_quantity(self, db_session, game_id, owner_id, resource_type):
        """Test updating a resource's quantity."""
        # Create a resource
        resource = Resource(
            game_id=game_id,
            owner_id=owner_id,
            resource_type_id=resource_type.id,
            quantity=100
        )
        
        db_session.add(resource)
        db_session.commit()
        
        # Update the quantity
        resource.quantity = 150
        db_session.commit()
        db_session.refresh(resource)
        
        # Verify the quantity was updated
        assert resource.quantity == 150