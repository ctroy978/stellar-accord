from unittest.mock import patch, MagicMock
# tests/services/test_technology_service.py
import pytest
from unittest.mock import patch, MagicMock
from app.services.technology_service import TechnologyService

@patch('app.services.technology_service.get_technology_config')
def test_check_development_prerequisites(mock_get_tech_config):
    """Test checking if a civilization can develop a technology."""
    # Setup mock
    mock_config = MagicMock()
    
    # Mock component lookup
    mock_config.components = {
        "power_conversion_system": MagicMock(name="Power Conversion System", tech_type="big_tech"),
        "dyson_sphere": MagicMock(name="Dyson Sphere", tech_type="universal_project"),
    }
    
    # Mock behavior for various test cases
    def mock_can_develop(civ, comp):
        if comp == "dyson_sphere":
            return False
        return True
    
    def mock_get_requirements(comp_id):
        if comp_id == "power_conversion_system":
            return [
                MagicMock(required_id="neutronium", required_type="resource", quantity=30),
                MagicMock(required_id="photon_crystal", required_type="resource", quantity=25),
                MagicMock(required_id="living_metal", required_type="resource", quantity=15)
            ]
        return []
    
    # Configure mock
    mock_config.can_civilization_develop.side_effect = mock_can_develop
    mock_config.get_development_requirements.side_effect = mock_get_requirements
    mock_get_tech_config.return_value = mock_config
    
    # Test with minimal info (capability check only)
    result = TechnologyService.check_development_prerequisites(
        "Thrizoth", "power_conversion_system"
    )
    assert result["can_develop"] is True
    
    # Test with resource info - sufficient resources
    result = TechnologyService.check_development_prerequisites(
        "Thrizoth", "power_conversion_system", 
        {
            "neutronium": 50,
            "photon_crystal": 50,
            "living_metal": 50
        }
    )
    assert result["can_develop"] is True
    
    # Test with resource info - insufficient resources
    result = TechnologyService.check_development_prerequisites(
        "Thrizoth", "power_conversion_system", 
        {
            "neutronium": 10,  # Not enough
            "photon_crystal": 50,
            "living_metal": 50
        }
    )
    assert result["can_develop"] is False
    assert "missing_requirements" in result
    
    # Test technology not available to civilization
    result = TechnologyService.check_development_prerequisites(
        "Thrizoth", "dyson_sphere"
    )
    assert result["can_develop"] is False
    
    # Test nonexistent technology - create a new mock config
    new_mock = MagicMock()
    new_mock.components = {}  # Empty components dict
    mock_get_tech_config.return_value = new_mock
    
    result = TechnologyService.check_development_prerequisites(
        "Thrizoth", "nonexistent_tech"
    )
    assert result["can_develop"] is False
    assert result["reason"] == "Technology not found"