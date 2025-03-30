# tests/services/test_technology_service.py
import pytest
from app.services.technology_service import TechnologyService

def test_get_available_technologies():
    """Test retrieving available technologies for a civilization."""
    # Get technologies for Thrizoth
    tech_list = TechnologyService.get_available_technologies("Thrizoth")
    
    # Verify structure of result
    assert "big_tech" in tech_list
    assert "uber_tech" in tech_list
    assert "universal_project" in tech_list
    
    # Verify we have some big_tech components
    assert len(tech_list["big_tech"]) > 0
    
    # Verify dyson_sphere is not included (Thrizoth is harmed by it)
    dyson_sphere_found = False
    for project in tech_list["universal_project"]:
        if project["id"] == "dyson_sphere":
            dyson_sphere_found = True
            break
    assert dyson_sphere_found is False
    
    # Get technologies for Silicon Liberation
    sl_tech_list = TechnologyService.get_available_technologies("Silicon Liberation")
    
    # Verify dyson_sphere IS included for Silicon Liberation (they benefit from it)
    dyson_sphere_found = False
    for project in sl_tech_list["universal_project"]:
        if project["id"] == "dyson_sphere":
            dyson_sphere_found = True
            break
    assert dyson_sphere_found is True

def test_get_technology_details():
    """Test retrieving technology details."""
    # Get details for a big tech component
    details = TechnologyService.get_technology_details("power_conversion_system")
    
    assert details["id"] == "power_conversion_system"
    assert details["name"] == "Power Conversion System"
    assert details["type"] == "big_tech"
    assert details["group"] == "A"
    assert len(details["requirements"]) > 0
    
    # Verify a requirement detail
    assert details["requirements"][0]["type"] == "resource"
    assert details["requirements"][0]["quantity"] > 0
    
    # Get details for a universal project
    details = TechnologyService.get_technology_details("dyson_sphere")
    
    assert details["id"] == "dyson_sphere"
    assert details["type"] == "universal_project"
    assert "effects" in details
    assert "beneficiaries" in details["effects"]
    
    # Test nonexistent technology
    details = TechnologyService.get_technology_details("nonexistent_tech")
    assert "error" in details

def test_check_development_prerequisites():
    """Test checking if a civilization can develop a technology."""
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
    
    # Test nonexistent technology
    result = TechnologyService.check_development_prerequisites(
        "Thrizoth", "nonexistent_tech"
    )
    assert result["can_develop"] is False
    assert result["reason"] == "Technology not found"

def test_get_project_effect():
    """Test retrieving project effects."""
    # Test beneficial effect
    effect = TechnologyService.get_project_effect("dyson_sphere", "Silicon Liberation")
    assert effect["effect"] == "beneficial"
    assert effect["points"] > 0
    
    # Test harmful effect
    effect = TechnologyService.get_project_effect("dyson_sphere", "Thrizoth")
    assert effect["effect"] == "harmful"
    assert effect["points"] < 0
    
    # Test neutral effect
    effect = TechnologyService.get_project_effect("dyson_sphere", "Methane Collective")
    assert effect["effect"] == "neutral"
    assert effect["points"] == 0