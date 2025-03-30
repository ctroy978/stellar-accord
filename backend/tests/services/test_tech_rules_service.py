# tests/services/test_tech_rules_service.py
import pytest
from unittest.mock import patch, MagicMock
from app.services.tech_rules_service import TechnologyService
from app.config.tech_rules import TechnologyConfig, TechComponent, TechRequirement

class TestTechnologyService:
    @patch('app.services.tech_rules_service.get_technology_config')  # Fix the path
    def test_get_available_technologies(self, mock_get_tech_config):
        """Test getting available technologies for a civilization."""
        # Setup mock config
        mock_config = MagicMock()
        mock_comp1 = MagicMock(
            component_id="comp1",
            name="Component 1",
            description="Description 1",
            tech_type="big_tech",
            tech_group="A"
        )
        mock_comp2 = MagicMock(
            component_id="comp2",
            name="Component 2",
            description="Description 2",
            tech_type="big_tech",
            tech_group="B"
        )

        mock_config.components = {
            "comp1": mock_comp1,
            "comp2": mock_comp2
        }

        # Set up can_civilization_develop to return True for comp1, False for comp2
        mock_config.can_civilization_develop.side_effect = lambda civ, comp: comp == "comp1"
        
        # The key fix - mock get_technologies_for_civilization
        mock_config.get_technologies_for_civilization.return_value = {
            "big_tech": [{"id": "comp1", "name": "Component 1"}]
        }

        mock_get_tech_config.return_value = mock_config

        # Test method
        result = TechnologyService.get_available_technologies("Thrizoth")

        # Should only include comp1
        assert len(result) == 1
    
    @patch('app.services.tech_rules_service.get_technology_config')
    def test_get_component_requirements(self, mock_get_tech_config):
        """Test getting component requirements."""
        # Setup mock config
        mock_config = MagicMock()
        mock_req1 = {"id": "req1", "type": "resource", "quantity": 10}
        mock_req2 = {"id": "req2", "type": "big_tech", "quantity": 1}

        mock_config.get_development_requirements.return_value = [
            MagicMock(required_id="req1", required_type="resource", quantity=10),
            MagicMock(required_id="req2", required_type="big_tech", quantity=1)
        ]

        mock_get_tech_config.return_value = mock_config

        # Test method
        result = TechnologyService.get_component_requirements("comp1")

        # Verify results
        assert len(result) == 2
        
        # Make sure the method was called
        mock_config.get_development_requirements.assert_called_once_with("comp1")
    
    @patch('app.services.tech_rules_service.get_technology_config')
    def test_check_development_prerequisites(self, mock_get_tech_config):
        """Test checking development prerequisites."""
        # Setup mock config
        mock_config = MagicMock()
        mock_comp = MagicMock(
            component_id="comp1",
            name="Component 1",
            description="Description 1",
            tech_type="big_tech",
            tech_group="A"
        )

        mock_config.components = {"comp1": mock_comp}
        mock_config.can_civilization_develop.return_value = True
        mock_config.get_development_requirements.return_value = [
            MagicMock(required_id="req1", required_type="resource", quantity=10)
        ]

        mock_get_tech_config.return_value = mock_config

        # Test method - positive case
        result = TechnologyService.check_development_prerequisites("Thrizoth", "comp1")

        # Verify results
        assert result["can_develop"] is True
        
        # Ensure method was called
        mock_config.can_civilization_develop.assert_called_with("Thrizoth", "comp1")