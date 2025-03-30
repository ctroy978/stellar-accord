# tests/config/test_tech_rules_config.py
import pytest
from app.config.tech_rules import TechnologyConfig, TechComponent, TechRequirement

class TestTechnologyConfig:
    def test_init_with_defaults(self):
        """Test initialization with defaults."""
        config = TechnologyConfig()
        assert hasattr(config, "components")
        assert hasattr(config, "requirements")
        assert hasattr(config, "civilization_capabilities")
    
    def test_can_civilization_develop(self):
        """Test civilization development capability check."""
        config = TechnologyConfig()
        
        # Add test components and capabilities
        test_component = TechComponent(
            component_id="test_component",
            name="Test Component",
            description="A test component",
            tech_type="big_tech",
            tech_group="A"
        )
        config.components["test_component"] = test_component
        
        # Set civilization capabilities
        config.civilization_capabilities = {
            "Thrizoth": ["A", "B", "C"],
            "Vasku": ["D", "E", "F"]
        }
        
        # Test positive case
        assert config.can_civilization_develop("Thrizoth", "test_component") is True
        
        # Test negative case
        assert config.can_civilization_develop("Vasku", "test_component") is False
        
        # Test non-existent component
        assert config.can_civilization_develop("Thrizoth", "nonexistent") is False
    
    def test_get_development_requirements(self):
        """Test getting development requirements."""
        config = TechnologyConfig()
        
        # Add test components and requirements
        test_component = TechComponent(
            component_id="test_component",
            name="Test Component",
            description="A test component",
            tech_type="big_tech",
            tech_group="A"
        )
        config.components["test_component"] = test_component
        
        test_req1 = TechRequirement(
            required_id="resource1",
            required_type="resource",
            quantity=10
        )
        test_req2 = TechRequirement(
            required_id="component2",
            required_type="big_tech",
            quantity=1
        )
        config.requirements["test_component"] = [test_req1, test_req2]
        
        # Test getting requirements
        requirements = config.get_development_requirements("test_component")
        assert len(requirements) == 2
        assert requirements[0].required_id == "resource1"
        assert requirements[0].quantity == 10
        assert requirements[1].required_id == "component2"
        
        # Test for non-existent component
        assert len(config.get_development_requirements("nonexistent")) == 0