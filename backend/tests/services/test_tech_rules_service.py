# tests/services/test_tech_rules_service.py
import pytest
from unittest.mock import patch, MagicMock
from app.services.tech_rules_service import TechnologyService
from app.config.tech_rules import TechnologyConfig, TechComponent, TechRequirement

class TestTechnologyService:
    @patch('app.services.technology_service.get_technology_config')
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
        
        mock_get_tech_config.return_value = mock_config
        
        # Test method
        result = TechnologyService.get_available_technologies("Thrizoth")
        
        # Should only include comp1
        assert len(result) == 1
        assert result[0]["component_id"] == "comp1"
        assert result[0]["name"] == "Component 1"
        
        # Verify calls
        mock_get_tech_config.assert_called_once()
        assert mock_config.can_civilization_develop.call_count == 2
    
    @patch('app.services.technology_service.get_technology_config')
    def test_get_component_requirements(self, mock_get_tech_config):
        """Test getting component requirements."""
        # Setup mock config
        mock_config = MagicMock()
        mock_req1 = MagicMock(required_id="req1", required_type="resource", quantity=10)
        mock_req2 = MagicMock(required_id="req2", required_type="big_tech", quantity=1)
        
        mock_config.get_development_requirements.return_value = [mock_req1, mock_req2]
        
        mock_get_tech_config.return_value = mock_config
        
        # Test method
        result = TechnologyService.get_component_requirements("comp1")
        
        # Verify results
        assert len(result) == 2
        assert result[0]["required_id"] == "req1"
        assert result[0]["required_type"] == "resource"
        assert result[0]["quantity"] == 10
        assert result[1]["required_id"] == "req2"
        
        # Verify calls
        mock_get_tech_config.assert_called_once()
        mock_config.get_development_requirements.assert_called_once_with("comp1")
    
    @patch('app.services.technology_service.get_technology_config')
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
        mock_req1 = MagicMock(required_id="req1", required_type="resource", quantity=10)
        
        mock_config.components = {"comp1": mock_comp}
        mock_config.can_civilization_develop.return_value = True
        mock_config.get_development_requirements.return_value = [mock_req1]
        
        mock_get_tech_config.return_value = mock_config
        
        # Test method - positive case
        result = TechnologyService.check_development_prerequisites("Thrizoth", "comp1")
        
        # Verify results
        assert result["can_develop"] is True
        assert result["component"]["component_id"] == "comp1"
        assert len(result["requirements"]) == 1
        assert result["requirements"][0]["required_id"] == "req1"
        
        # Test method - civilization cannot develop
        mock_config.can_civilization_develop.return_value = False
        
        result = TechnologyService.check_development_prerequisites("Vasku", "comp1")
        
        assert result["can_develop"] is False
        assert "reason" in result
        
        # Test method - component does not exist
        mock_config.can_civilization_develop.return_value = True
        mock_config.components = {}
        
        result = TechnologyService.check_development_prerequisites("Thrizoth", "nonexistent")
        
        assert result["can_develop"] is False
        assert "reason" in result