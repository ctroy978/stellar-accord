# tests/config/test_technology.py
import pytest
from uuid import uuid4
from app.config.technology import TechComponent, TechRequirement, TechnologyConfig

def test_tech_component_creation_and_serialization():
    """Test that tech components can be created and serialized correctly."""
    # Create a component
    component = TechComponent(
        component_id="quantum_core",
        name="Quantum Core",
        description="Advanced quantum processing unit",
        tech_type="big_tech",
        tech_group="B",
        civilization_restrictions=["Thrizoth"]
    )
    
    # Verify attributes
    assert component.component_id == "quantum_core"
    assert component.name == "Quantum Core"
    assert component.tech_type == "big_tech"
    assert component.tech_group == "B"
    assert component.civilization_restrictions == ["Thrizoth"]
    
    # Test serialization
    data = component.to_dict()
    assert data["component_id"] == "quantum_core"
    assert data["name"] == "Quantum Core"
    
    # Test deserialization
    recreated = TechComponent.from_dict(data)
    assert recreated.component_id == component.component_id
    assert recreated.name == component.name
    assert recreated.tech_group == component.tech_group
    assert recreated.civilization_restrictions == component.civilization_restrictions

def test_tech_requirement_creation_and_serialization():
    """Test that tech requirements can be created and serialized correctly."""
    # Create a requirement
    requirement = TechRequirement(
        required_id="neutronium",
        required_type="resource",
        quantity=30
    )
    
    # Verify attributes
    assert requirement.required_id == "neutronium"
    assert requirement.required_type == "resource"
    assert requirement.quantity == 30
    
    # Test serialization
    data = requirement.to_dict()
    assert data["required_id"] == "neutronium"
    assert data["quantity"] == 30
    
    # Test deserialization
    recreated = TechRequirement.from_dict(data)
    assert recreated.required_id == requirement.required_id
    assert recreated.required_type == requirement.required_type
    assert recreated.quantity == requirement.quantity

def test_tech_requirement_minimum_quantity():
    """Test that quantity is at least 1."""
    requirement = TechRequirement(
        required_id="resource1",
        required_type="resource",
        quantity=0  # Invalid, should be set to 1
    )
    assert requirement.quantity == 1
    
    requirement = TechRequirement(
        required_id="resource1",
        required_type="resource",
        quantity=-5  # Invalid, should be set to 1
    )
    assert requirement.quantity == 1

def test_technology_config_initialization():
    """Test that the technology configuration initializes with defaults."""
    config = TechnologyConfig(config_id=uuid4())
    
    # Verify basic structure
    assert isinstance(config.components, dict)
    assert isinstance(config.requirements, dict)
    assert isinstance(config.civilization_capabilities, dict)
    assert isinstance(config.project_effects, dict)
    
    # Verify some content was loaded
    assert len(config.components) > 0
    assert len(config.requirements) > 0
    assert len(config.civilization_capabilities) > 0
    
    # Verify a specific component exists
    assert "power_conversion_system" in config.components
    pcs = config.components["power_conversion_system"]
    assert pcs.name == "Power Conversion System"
    assert pcs.tech_type == "big_tech"
    assert pcs.tech_group == "A"

def test_technology_config_serialization():
    """Test that the config can be serialized and deserialized."""
    original = TechnologyConfig(config_id=uuid4())
    
    # Add a custom component for testing
    original.components["test_component"] = TechComponent(
        component_id="test_component",
        name="Test Component",
        description="A test component",
        tech_type="big_tech",
        tech_group="Z"
    )
    
    # Serialize
    data = original.to_dict()
    
    # Deserialize
    recreated = TechnologyConfig.from_dict(data)
    
    # Verify components match
    assert len(recreated.components) == len(original.components)
    assert "test_component" in recreated.components
    test_component = recreated.components["test_component"]
    assert test_component.name == "Test Component"
    assert test_component.tech_group == "Z"
    
    # Verify requirements match
    assert len(recreated.requirements) == len(original.requirements)
    
    # Verify civilization capabilities match
    assert recreated.civilization_capabilities == original.civilization_capabilities

def test_can_civilization_develop():
    """Test the logic for determining if a civilization can develop a technology."""
    config = TechnologyConfig()
    
    # Test regular group-based restrictions
    # Thrizoth can develop Group A tech
    assert config.can_civilization_develop("Thrizoth", "power_conversion_system") is True
    
    # Create a Group F tech (which Thrizoth can't develop)
    config.components["group_f_tech"] = TechComponent(
        component_id="group_f_tech",
        name="Group F Technology",
        description="A technology in group F",
        tech_type="big_tech",
        tech_group="F"
    )
    
    # Thrizoth can't develop group F tech
    assert config.can_civilization_develop("Thrizoth", "group_f_tech") is False
    # Vasku can develop group F tech
    assert config.can_civilization_develop("Vasku", "group_f_tech") is True
    
    # Test civilization-specific restrictions
    config.components["thrizoth_restricted_tech"] = TechComponent(
        component_id="thrizoth_restricted_tech",
        name="Thrizoth Restricted Tech",
        description="Tech restricted from Thrizoth",
        tech_type="big_tech",
        tech_group="A",
        civilization_restrictions=["Thrizoth"]
    )
    
    assert config.can_civilization_develop("Thrizoth", "thrizoth_restricted_tech") is False
    assert config.can_civilization_develop("Vasku", "thrizoth_restricted_tech") is True
    
    # Test universal project restrictions
    # Thrizoth is harmed by Dyson Sphere, so cannot develop it
    assert config.can_civilization_develop("Thrizoth", "dyson_sphere") is False
    # Silicon Liberation benefits from Dyson Sphere, so can develop it
    assert config.can_civilization_develop("Silicon Liberation", "dyson_sphere") is True

def test_get_development_requirements():
    """Test retrieving requirements for a technology."""
    config = TechnologyConfig()
    
    # Test retrieving requirements for a component with requirements
    requirements = config.get_development_requirements("power_conversion_system")
    assert len(requirements) == 3
    
    # Check specific requirement details
    assert requirements[0].required_id == "neutronium"
    assert requirements[0].required_type == "resource"
    assert requirements[0].quantity == 30
    
    # Test retrieving requirements for a non-existent component
    requirements = config.get_development_requirements("nonexistent_component")
    assert len(requirements) == 0

def test_get_project_effect():
    """Test retrieving project effects for a civilization."""
    config = TechnologyConfig()
    
    # Test beneficial effect
    effect = config.get_project_effect("dyson_sphere", "Silicon Liberation")
    assert effect["effect"] == "beneficial"
    assert effect["points"] == 1
    
    # Test harmful effect
    effect = config.get_project_effect("dyson_sphere", "Thrizoth")
    assert effect["effect"] == "harmful"
    assert effect["points"] == -1
    
    # Test neutral effect
    effect = config.get_project_effect("dyson_sphere", "Methane Collective")
    assert effect["effect"] == "neutral"
    assert effect["points"] == 0
    
    # Test non-existent project
    effect = config.get_project_effect("nonexistent_project", "Thrizoth")
    assert effect["effect"] == "none"
    assert effect["points"] == 0

def test_get_technologies_for_civilization():
    """Test retrieving available technologies for a civilization."""
    config = TechnologyConfig()
    
    # Get technologies for Thrizoth
    tech_list = config.get_technologies_for_civilization("Thrizoth")
    
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
    sl_tech_list = config.get_technologies_for_civilization("Silicon Liberation")
    
    # Verify structure of result for Silicon Liberation
    assert "big_tech" in sl_tech_list
    assert "uber_tech" in sl_tech_list
    assert "universal_project" in sl_tech_list
    
    # Verify dyson_sphere IS included for Silicon Liberation (they benefit from it)
    dyson_sphere_found = False
    for project in sl_tech_list["universal_project"]:
        if project["id"] == "dyson_sphere":
            dyson_sphere_found = True
            break
    assert dyson_sphere_found is True