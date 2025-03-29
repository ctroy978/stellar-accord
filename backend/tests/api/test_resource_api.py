# File: tests/api/test_resource_api.py
import pytest
import uuid
from fastapi.testclient import TestClient

from app.schemas.enums import ResourceCategory, ResourceRarity
from app.crud import resource as crud_resource

class TestResourceTypeAPI:
    """Tests for ResourceType API endpoints."""
    
    def test_get_resource_types(self, client, db_session):
        """Test getting all resource types."""
        # Create some resource types
        resource_type1 = {
            "name": "API Test Resource 1",
            "category": ResourceCategory.RAW_MATERIAL,
            "rarity": ResourceRarity.COMMON,
            "description": "A test resource type",
            "producible_by": ["Thrizoth", "Methane Collective"]
        }
        
        resource_type2 = {
            "name": "API Test Resource 2",
            "category": ResourceCategory.TECHNOLOGY,
            "rarity": ResourceRarity.RARE,
            "description": "Another test resource type",
            "producible_by": ["Silicon Liberation", "Kyrathi"]
        }
        
        # Add resource types to the database
        response1 = client.post("/api/resources/types/", json=resource_type1)
        response2 = client.post("/api/resources/types/", json=resource_type2)
        
        # Verify the resource types were created
        assert response1.status_code == 201
        assert response2.status_code == 201
        
        # Get all resource types
        response = client.get("/api/resources/types/")
        
        # Verify the response
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        
        # Find our created resource types in the response
        created_types = [rt for rt in response.json() if rt["name"] in ["API Test Resource 1", "API Test Resource 2"]]
        assert len(created_types) == 2
    
    def test_create_resource_type(self, client, db_session):
        """Test creating a resource type."""
        # Resource type data
        resource_type = {
            "name": "API Create Resource",
            "category": ResourceCategory.ENERGY_SOURCE,
            "rarity": ResourceRarity.VERY_RARE,
            "description": "A resource type created via API",
            "producible_by": ["Vasku", "Glacian Current"]
        }
        
        # Create the resource type
        response = client.post("/api/resources/types/", json=resource_type)
        
        # Verify the response
        assert response.status_code == 201
        assert response.json()["name"] == "API Create Resource"
        assert response.json()["category"] == ResourceCategory.ENERGY_SOURCE
        assert response.json()["rarity"] == ResourceRarity.VERY_RARE
        assert response.json()["description"] == "A resource type created via API"
        assert response.json()["producible_by"] == ["Vasku", "Glacian Current"]
    
    def test_get_resource_type(self, client, db_session):
        """Test getting a specific resource type by ID."""
        # Create a resource type
        resource_type = {
            "name": "API Get Resource",
            "category": ResourceCategory.INFORMATION,
            "rarity": ResourceRarity.UNCOMMON
        }
        
        # Add the resource type to the database
        response = client.post("/api/resources/types/", json=resource_type)
        resource_type_id = response.json()["id"]
        
        # Get the resource type
        response = client.get(f"/api/resources/types/{resource_type_id}")
        
        # Verify the response
        assert response.status_code == 200
        assert response.json()["id"] == resource_type_id
        assert response.json()["name"] == "API Get Resource"
    
    def test_update_resource_type(self, client, db_session):
        """Test updating a resource type."""
        # Create a resource type
        resource_type = {
            "name": "API Update Resource",
            "category": ResourceCategory.CULTURAL_ITEM,
            "rarity": ResourceRarity.COMMON
        }
        
        # Add the resource type to the database
        response = client.post("/api/resources/types/", json=resource_type)
        resource_type_id = response.json()["id"]
        
        # Update data
        update_data = {
            "description": "Updated description",
            "producible_by": ["Thrizoth"]
        }
        
        # Update the resource type
        response = client.put(f"/api/resources/types/{resource_type_id}", json=update_data)
        
        # Verify the response
        assert response.status_code == 200
        assert response.json()["id"] == resource_type_id
        assert response.json()["name"] == "API Update Resource"  # Unchanged
        assert response.json()["description"] == "Updated description"
        assert response.json()["producible_by"] == ["Thrizoth"]
    
    def test_delete_resource_type(self, client, db_session):
        """Test deleting a resource type."""
        # Create a resource type
        resource_type = {
            "name": "API Delete Resource",
            "category": ResourceCategory.REFINED_MATERIAL,
            "rarity": ResourceRarity.COMMON
        }
        
        # Add the resource type to the database
        response = client.post("/api/resources/types/", json=resource_type)
        resource_type_id = response.json()["id"]
        
        # Delete the resource type
        response = client.delete(f"/api/resources/types/{resource_type_id}")
        
        # Verify the response
        assert response.status_code == 204
        
        # Try to get the deleted resource type
        response = client.get(f"/api/resources/types/{resource_type_id}")
        
        # It should return a 404 Not Found
        assert response.status_code == 404

class TestResourceAPI:
    """Tests for Resource API endpoints."""
    
    @pytest.fixture
    def game_id(self):
        """Generate a game ID for testing."""
        return str(uuid.uuid4())
    
    @pytest.fixture
    def civilization_id(self):
        """Generate a civilization ID for testing."""
        return str(uuid.uuid4())
    
    @pytest.fixture
    def resource_type_id(self, client):
        """Create a resource type and return its ID."""
        # Create a resource type
        resource_type = {
            "name": "API Resource Test Type",
            "category": ResourceCategory.RAW_MATERIAL,
            "rarity": ResourceRarity.COMMON
        }
        
        # Add the resource type to the database
        response = client.post("/api/resources/types/", json=resource_type)
        return response.json()["id"]
    
    def test_get_civilization_resources(self, client, db_session, game_id, civilization_id, resource_type_id):
        """Test getting all resources owned by a civilization."""
        # Add resources to the civilization's inventory
        resource_data = {
            "resource_type_id": resource_type_id,
            "quantity": 100
        }
        
        response = client.post(
            f"/api/resources/game/{game_id}/civilization/{civilization_id}",
            json=resource_data
        )
        
        # Verify the resources were added
        assert response.status_code == 200
        
        # Get the civilization's resources
        response = client.get(f"/api/resources/game/{game_id}/civilization/{civilization_id}")
        
        # Verify the response
        assert response.status_code == 200
        resources = response.json()
        assert isinstance(resources, list)
        assert len(resources) == 1
        assert resources[0]["resource_type_id"] == resource_type_id
        assert resources[0]["quantity"] == 100
    
    def test_add_resources(self, client, db_session, game_id, civilization_id, resource_type_id):
        """Test adding resources to a civilization's inventory."""
        # Resource data
        resource_data = {
            "resource_type_id": resource_type_id,
            "quantity": 50
        }
        
        # Add resources
        response = client.post(
            f"/api/resources/game/{game_id}/civilization/{civilization_id}",
            json=resource_data
        )
        
        # Verify the response
        assert response.status_code == 200
        assert response.json()["resource_type_id"] == resource_type_id
        assert response.json()["quantity"] == 50
        
        # Add more resources
        resource_data["quantity"] = 25
        response = client.post(
            f"/api/resources/game/{game_id}/civilization/{civilization_id}",
            json=resource_data
        )
        
        # Verify the resources were added to the existing total
        assert response.status_code == 200
        assert response.json()["quantity"] == 75
    
    def test_update_resource_quantity(self, client, db_session, game_id, civilization_id, resource_type_id):
        """Test updating a resource's quantity."""
        # Add initial resources
        resource_data = {
            "resource_type_id": resource_type_id,
            "quantity": 100
        }
        
        client.post(
            f"/api/resources/game/{game_id}/civilization/{civilization_id}",
            json=resource_data
        )
        
        # Update the quantity
        update_data = {
            "quantity": 200
        }
        
        response = client.put(
            f"/api/resources/game/{game_id}/civilization/{civilization_id}/resource/{resource_type_id}",
            json=update_data
        )
        
        # Verify the response
        assert response.status_code == 200
        assert response.json()["quantity"] == 200
    
    def test_remove_resources(self, client, db_session, game_id, civilization_id, resource_type_id):
        """Test removing resources from a civilization's inventory."""
        # Add initial resources
        resource_data = {
            "resource_type_id": resource_type_id,
            "quantity": 100
        }
        
        client.post(
            f"/api/resources/game/{game_id}/civilization/{civilization_id}",
            json=resource_data
        )
        
        # Remove some resources
        response = client.delete(
            f"/api/resources/game/{game_id}/civilization/{civilization_id}/resource/{resource_type_id}?quantity=30"
        )
        
        # Verify the response
        assert response.status_code == 200
        assert response.json()["quantity"] == 70
    
    def test_remove_too_many_resources(self, client, db_session, game_id, civilization_id, resource_type_id):
        """Test that removing more resources than available returns an error."""
        # Add initial resources
        resource_data = {
            "resource_type_id": resource_type_id,
            "quantity": 50
        }
        
        client.post(
            f"/api/resources/game/{game_id}/civilization/{civilization_id}",
            json=resource_data
        )
        
        # Try to remove more resources than available
        response = client.delete(
            f"/api/resources/game/{game_id}/civilization/{civilization_id}/resource/{resource_type_id}?quantity=100"
        )
        
        # Verify the response
        assert response.status_code == 400
        assert "Insufficient resources" in response.json()["detail"]