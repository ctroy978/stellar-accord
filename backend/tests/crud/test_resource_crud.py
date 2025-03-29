# File: tests/crud/test_resource_crud.py
import pytest
import uuid
from fastapi import HTTPException

from app.crud import resource as crud_resource
from app.models.resource import ResourceType, Resource
from app.schemas.resource import ResourceTypeCreate, ResourceTypeUpdate, ResourceCreate, ResourceUpdate
from app.schemas.enums import ResourceCategory, ResourceRarity

class TestResourceTypeCRUD:
    """Tests for ResourceType CRUD operations."""
    
    def test_create_resource_type(self, db_session):
        """Test creating a resource type."""
        # Create a resource type using the CRUD function
        resource_type_data = ResourceTypeCreate(
            name="New Resource Type",
            category=ResourceCategory.TECHNOLOGY,
            rarity=ResourceRarity.RARE,
            description="A new resource type",
            producible_by=["Kyrathi", "Silicon Liberation"]
        )
        
        resource_type = crud_resource.create_resource_type(db_session, resource_type=resource_type_data)
        
        # Verify the resource type was created
        assert resource_type.id is not None
        assert resource_type.name == "New Resource Type"
        assert resource_type.category == ResourceCategory.TECHNOLOGY
        assert resource_type.rarity == ResourceRarity.RARE
        assert resource_type.description == "A new resource type"
        assert resource_type.producible_by == ["Kyrathi", "Silicon Liberation"]
        
        # Verify it exists in the database
        db_resource_type = crud_resource.get_resource_type_by_name(db_session, name="New Resource Type")
        assert db_resource_type is not None
        assert db_resource_type.id == resource_type.id
    
    def test_get_resource_type(self, db_session):
        """Test getting a resource type by ID."""
        # Create a resource type
        resource_type_data = ResourceTypeCreate(
            name="Resource To Get",
            category=ResourceCategory.ENERGY_SOURCE,
            rarity=ResourceRarity.UNCOMMON
        )
        
        created_type = crud_resource.create_resource_type(db_session, resource_type=resource_type_data)
        
        # Get the resource type by ID
        retrieved_type = crud_resource.get_resource_type(db_session, resource_type_id=created_type.id)
        
        # Verify the resource type was retrieved
        assert retrieved_type is not None
        assert retrieved_type.id == created_type.id
        assert retrieved_type.name == "Resource To Get"
    
    def test_update_resource_type(self, db_session):
        """Test updating a resource type."""
        # Create a resource type
        resource_type_data = ResourceTypeCreate(
            name="Resource To Update",
            category=ResourceCategory.INFORMATION,
            rarity=ResourceRarity.VERY_RARE
        )
        
        created_type = crud_resource.create_resource_type(db_session, resource_type=resource_type_data)
        
        # Update the resource type
        update_data = ResourceTypeUpdate(
            description="Updated description",
            producible_by=["Vasku"]
        )
        
        updated_type = crud_resource.update_resource_type(
            db_session, 
            resource_type_id=created_type.id, 
            resource_type=update_data
        )
        
        # Verify the resource type was updated
        assert updated_type.description == "Updated description"
        assert updated_type.producible_by == ["Vasku"]
        assert updated_type.name == "Resource To Update"  # Unchanged field
    
    def test_delete_resource_type(self, db_session):
        """Test deleting a resource type."""
        # Create a resource type
        resource_type_data = ResourceTypeCreate(
            name="Resource To Delete",
            category=ResourceCategory.CULTURAL_ITEM,
            rarity=ResourceRarity.COMMON
        )
        
        created_type = crud_resource.create_resource_type(db_session, resource_type=resource_type_data)
        
        # Delete the resource type
        crud_resource.delete_resource_type(db_session, resource_type_id=created_type.id)
        
        # Verify the resource type was deleted
        deleted_type = crud_resource.get_resource_type(db_session, resource_type_id=created_type.id)
        assert deleted_type is None

class TestResourceCRUD:
    """Tests for Resource CRUD operations."""
    
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
    def civilization_id(self):
        """Generate a civilization ID for testing."""
        return uuid.uuid4()
    
    @pytest.fixture
    def resource_type(self, db_session):
        """Create a resource type for testing."""
        resource_type_data = ResourceTypeCreate(
            name="Test Resource",
            category=ResourceCategory.RAW_MATERIAL,
            rarity=ResourceRarity.COMMON
        )
        
        return crud_resource.create_resource_type(db_session, resource_type=resource_type_data)
    
    def test_add_resources(self, db_session, game_id, civilization_id, resource_type):
        """Test adding resources to a civilization's inventory."""
        # Add resources
        resource_data = ResourceCreate(
            resource_type_id=resource_type.id,
            quantity=100
        )
        
        added_resource = crud_resource.add_resources(
            db_session, 
            game_id=game_id,
            civilization_id=civilization_id,
            resource=resource_data
        )
        
        # Verify the resources were added
        assert added_resource.game_id == game_id
        assert added_resource.owner_id == civilization_id
        assert added_resource.resource_type_id == resource_type.id
        assert added_resource.quantity == 100
        
        # Add more of the same resource
        more_resource_data = ResourceCreate(
            resource_type_id=resource_type.id,
            quantity=50
        )
        
        updated_resource = crud_resource.add_resources(
            db_session, 
            game_id=game_id,
            civilization_id=civilization_id,
            resource=more_resource_data
        )
        
        # Verify the resources were added to the existing total
        assert updated_resource.quantity == 150
    
    def test_get_civilization_resources(self, db_session, game_id, civilization_id, resource_type):
        """Test getting all resources owned by a civilization."""
        # Add resources
        resource_data = ResourceCreate(
            resource_type_id=resource_type.id,
            quantity=100
        )
        
        crud_resource.add_resources(
            db_session, 
            game_id=game_id,
            civilization_id=civilization_id,
            resource=resource_data
        )
        
        # Get civilization resources
        resources = crud_resource.get_civilization_resources(
            db_session,
            game_id=game_id,
            civilization_id=civilization_id
        )
        
        # Verify the resources were retrieved
        assert len(resources) == 1
        assert resources[0].resource_type_id == resource_type.id
        assert resources[0].quantity == 100
    
    def test_update_resource_quantity(self, db_session, game_id, civilization_id, resource_type):
        """Test updating a resource's quantity."""
        # Add resources
        resource_data = ResourceCreate(
            resource_type_id=resource_type.id,
            quantity=100
        )
        
        crud_resource.add_resources(
            db_session, 
            game_id=game_id,
            civilization_id=civilization_id,
            resource=resource_data
        )
        
        # Update the quantity
        update_data = ResourceUpdate(quantity=200)
        
        updated_resource = crud_resource.update_resource_quantity(
            db_session,
            game_id=game_id,
            civilization_id=civilization_id,
            resource_type_id=resource_type.id,
            update=update_data
        )
        
        # Verify the quantity was updated
        assert updated_resource.quantity == 200
    
    def test_remove_resources(self, db_session, game_id, civilization_id, resource_type):
        """Test removing resources from a civilization's inventory."""
        # Add resources
        resource_data = ResourceCreate(
            resource_type_id=resource_type.id,
            quantity=100
        )
        
        crud_resource.add_resources(
            db_session, 
            game_id=game_id,
            civilization_id=civilization_id,
            resource=resource_data
        )
        
        # Remove some resources
        result = crud_resource.remove_resources(
            db_session,
            game_id=game_id,
            civilization_id=civilization_id,
            resource_type_id=resource_type.id,
            quantity=30
        )
        
        # Verify the resources were removed
        assert result.quantity == 70
    
    def test_remove_too_many_resources(self, db_session, game_id, civilization_id, resource_type):
        """Test removing more resources than available raises an error."""
        # Add resources
        resource_data = ResourceCreate(
            resource_type_id=resource_type.id,
            quantity=50
        )
        
        crud_resource.add_resources(
            db_session, 
            game_id=game_id,
            civilization_id=civilization_id,
            resource=resource_data
        )
        
        # Try to remove more resources than available
        with pytest.raises(HTTPException) as excinfo:
            crud_resource.remove_resources(
                db_session,
                game_id=game_id,
                civilization_id=civilization_id,
                resource_type_id=resource_type.id,
                quantity=100
            )
        
        # Verify the error
        assert excinfo.value.status_code == 400
        assert "Insufficient resources" in excinfo.value.detail