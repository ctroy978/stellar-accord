# File: tests/integration/test_api_integration.py
import pytest
import uuid
from fastapi.testclient import TestClient

from app.schemas.enums import ResourceCategory, ResourceRarity, CivilizationName, GameStatus

class TestGameSetupWorkflow:
    """Test the complete game setup workflow through the API."""
    
    def test_complete_game_setup(self, client, db_session):
        """Test creating a game, adding civilizations, and initializing resources."""
        # Step 1: Create a new game
        game_data = {
            "name": "Integration Test Game"
        }
        
        response = client.post("/api/games/", json=game_data)
        assert response.status_code == 201
        game = response.json()
        game_id = game["id"]
        assert game["name"] == "Integration Test Game"
        assert game["status"] == GameStatus.SETUP
        
        # Step 2: Create civilizations for the game
        civ1_data = {
            "game_id": game_id,
            "name": CivilizationName.THRIZOTH,
            "display_name": "The Thrizoth Empire",
            "description": "Plant-like beings with distributed consciousness",
            "homeworld": "Verdant",
            "system_code": "CD"
        }
        
        civ2_data = {
            "game_id": game_id,
            "name": CivilizationName.METHANE_COLLECTIVE,
            "display_name": "The Methane Collective",
            "description": "Methane-breathing entities with collective intelligence",
            "homeworld": "Amalgus",
            "system_code": "IJ"
        }
        
        response1 = client.post("/api/civilizations/", json=civ1_data)
        response2 = client.post("/api/civilizations/", json=civ2_data)
        
        assert response1.status_code == 201
        assert response2.status_code == 201
        
        civ1_id = response1.json()["id"]
        civ2_id = response2.json()["id"]
        
        # Step 3: Define resource types
        resource_type1 = {
            "name": "Neutronium",
            "category": ResourceCategory.RAW_MATERIAL,
            "rarity": ResourceRarity.RARE,
            "description": "A rare and valuable metallic element",
            "producible_by": [CivilizationName.THRIZOTH, CivilizationName.KYRATHI]
        }
        
        resource_type2 = {
            "name": "Quantum Particles",
            "category": ResourceCategory.RAW_MATERIAL,
            "rarity": ResourceRarity.UNCOMMON,
            "description": "Subatomic particles with quantum properties",
            "producible_by": [CivilizationName.METHANE_COLLECTIVE, CivilizationName.VASKU]
        }
        
        response1 = client.post("/api/resources/types/", json=resource_type1)
        response2 = client.post("/api/resources/types/", json=resource_type2)
        
        assert response1.status_code == 201
        assert response2.status_code == 201
        
        rt1_id = response1.json()["id"]
        rt2_id = response2.json()["id"]
        
        # Step 4: Assign initial resources to civilizations
        resource1_data = {
            "resource_type_id": rt1_id,
            "quantity": 100
        }
        
        resource2_data = {
            "resource_type_id": rt2_id,
            "quantity": 75
        }
        
        # Assign resources to first civilization
        response = client.post(f"/api/resources/game/{game_id}/civilization/{civ1_id}", json=resource1_data)
        assert response.status_code == 200
        
        # Assign resources to second civilization
        response = client.post(f"/api/resources/game/{game_id}/civilization/{civ2_id}", json=resource2_data)
        assert response.status_code == 200
        
        # Step 5: Start the game
        update_game_data = {
            "status": GameStatus.ACTIVE
        }
        
        response = client.patch(f"/api/games/{game_id}", json=update_game_data)
        assert response.status_code == 200
        assert response.json()["status"] == GameStatus.ACTIVE
        
        # Step 6: Verify game setup
        # Check that the game exists and is active
        response = client.get(f"/api/games/{game_id}")
        assert response.status_code == 200
        assert response.json()["status"] == GameStatus.ACTIVE
        
        # Check that civilizations exist
        response = client.get(f"/api/civilizations/game/{game_id}")
        assert response.status_code == 200
        civilizations = response.json()
        assert len(civilizations) == 2
        
        # Check that resources are assigned
        response = client.get(f"/api/resources/game/{game_id}/civilization/{civ1_id}")
        assert response.status_code == 200
        resources = response.json()
        assert len(resources) == 1
        assert resources[0]["quantity"] == 100
        
        response = client.get(f"/api/resources/game/{game_id}/civilization/{civ2_id}")
        assert response.status_code == 200
        resources = response.json()
        assert len(resources) == 1
        assert resources[0]["quantity"] == 75


class TestResourceTradingWorkflow:
    """Test the resource trading workflow through the API."""
    
    @pytest.fixture
    def setup_game_with_civilizations(self, client, db_session):
        """Set up a game with civilizations and resources for testing."""
        # Create a game
        game_data = {"name": "Resource Trading Test Game"}
        game_response = client.post("/api/games/", json=game_data)
        game_id = game_response.json()["id"]
        
        # Create civilizations
        civ1_data = {
            "game_id": game_id,
            "name": CivilizationName.SILICON_LIBERATION,
            "display_name": "The Silicon Liberation"
        }
        
        civ2_data = {
            "game_id": game_id,
            "name": CivilizationName.GLACIAN_CURRENT,
            "display_name": "The Glacian Current"
        }
        
        civ1_response = client.post("/api/civilizations/", json=civ1_data)
        civ2_response = client.post("/api/civilizations/", json=civ2_data)
        
        civ1_id = civ1_response.json()["id"]
        civ2_id = civ2_response.json()["id"]
        
        # Create resource types
        resource_type1 = {
            "name": "Advanced Computing",
            "category": ResourceCategory.TECHNOLOGY,
            "rarity": ResourceRarity.RARE,
            "producible_by": [CivilizationName.SILICON_LIBERATION]
        }
        
        resource_type2 = {
            "name": "Water Purification",
            "category": ResourceCategory.TECHNOLOGY,
            "rarity": ResourceRarity.UNCOMMON,
            "producible_by": [CivilizationName.GLACIAN_CURRENT]
        }
        
        rt1_response = client.post("/api/resources/types/", json=resource_type1)
        rt2_response = client.post("/api/resources/types/", json=resource_type2)
        
        rt1_id = rt1_response.json()["id"]
        rt2_id = rt2_response.json()["id"]
        
        # Add resources to civilizations
        client.post(
            f"/api/resources/game/{game_id}/civilization/{civ1_id}",
            json={"resource_type_id": rt1_id, "quantity": 50}
        )
        
        client.post(
            f"/api/resources/game/{game_id}/civilization/{civ2_id}",
            json={"resource_type_id": rt2_id, "quantity": 50}
        )
        
        # Start the game
        client.patch(f"/api/games/{game_id}", json={"status": GameStatus.ACTIVE})
        
        return {
            "game_id": game_id,
            "civ1_id": civ1_id,
            "civ2_id": civ2_id,
            "rt1_id": rt1_id,
            "rt2_id": rt2_id
        }
    
    def test_resource_trading(self, client, db_session, setup_game_with_civilizations):
        """Test trading resources between civilizations."""
        game_id = setup_game_with_civilizations["game_id"]
        civ1_id = setup_game_with_civilizations["civ1_id"]
        civ2_id = setup_game_with_civilizations["civ2_id"]
        rt1_id = setup_game_with_civilizations["rt1_id"]
        rt2_id = setup_game_with_civilizations["rt2_id"]
        
        # Create a trade
        trade_data = {
            "game_id": game_id,
            "resource_type_id": rt1_id,
            "quantity": 20,
            "sender_id": civ1_id,
            "receiver_id": civ2_id,
            "hub_id": "Alpha"
        }
        
        response = client.post("/api/trades/", json=trade_data)
        assert response.status_code == 201
        trade = response.json()
        assert trade["resource_type_id"] == rt1_id
        assert trade["quantity"] == 20
        assert trade["sender_id"] == civ1_id
        assert trade["receiver_id"] == civ2_id
        
        # Execute the trade (normally happens during cleanup phase)
        response = client.post(f"/api/trades/{trade['id']}/execute")
        assert response.status_code == 200
        
        # Verify the resources were transferred
        response = client.get(f"/api/resources/game/{game_id}/civilization/{civ1_id}")
        civ1_resources = response.json()
        rt1_resource = next((r for r in civ1_resources if r["resource_type_id"] == rt1_id), None)
        assert rt1_resource["quantity"] == 30  # 50 - 20
        
        response = client.get(f"/api/resources/game/{game_id}/civilization/{civ2_id}")
        civ2_resources = response.json()
        rt1_resource = next((r for r in civ2_resources if r["resource_type_id"] == rt1_id), None)
        assert rt1_resource["quantity"] == 18 # 20-10% delivery cost
        
        # Create a return trade
        trade_data = {
            "game_id": game_id,
            "resource_type_id": rt2_id,
            "quantity": 15,
            "sender_id": civ2_id,
            "receiver_id": civ1_id,
            "hub_id": "Beta"
        }
        
        response = client.post("/api/trades/", json=trade_data)
        assert response.status_code == 201
        trade = response.json()
        
        # Execute the return trade
        response = client.post(f"/api/trades/{trade['id']}/execute")
        assert response.status_code == 200
        
        # Verify the resources were transferred
        response = client.get(f"/api/resources/game/{game_id}/civilization/{civ2_id}")
        civ2_resources = response.json()
        rt2_resource = next((r for r in civ2_resources if r["resource_type_id"] == rt2_id), None)
        assert rt2_resource["quantity"] == 35  # 50 - 15
        
        response = client.get(f"/api/resources/game/{game_id}/civilization/{civ1_id}")
        civ1_resources = response.json()
        rt2_resource = next((r for r in civ1_resources if r["resource_type_id"] == rt2_id), None)
        assert rt2_resource["quantity"] == 13 #15 - 10% delivery