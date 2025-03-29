# tests/config/test_validation.py
import pytest
from app.config.star_map import StarMapConfig, StarSystem

def test_star_map_validation():
    """Test the validation function of StarMapConfig."""
    # Create a minimally valid configuration
    config = StarMapConfig()
    
    # Intentionally empty the systems and connections to start with a clean slate
    config.systems = {}
    config.connections = {}
    
    # Add a valid system
    system = StarSystem(
        system_id="TEST",
        name="Test System",
        position=(100, 100)
    )
    config.systems["TEST"] = system
    
    # No connections yet, should still be valid
    assert config.validate() is True
    
    # Add a valid connection
    config.connections["TEST"] = []
    assert config.validate() is True
    
    # Invalid position type
    invalid_system = StarSystem(
        system_id="INVALID",
        name="Invalid System",
        position="not a tuple"  # Invalid position
    )
    config.systems["INVALID"] = invalid_system
    assert config.validate() is False
    
    # Fix the system
    config.systems["INVALID"].position = (200, 200)
    assert config.validate() is True
    
    # Invalid connection (references non-existent system)
    config.connections["TEST"] = ["NONEXISTENT"]
    assert config.validate() is False
    
    # Fix the connection
    config.connections["TEST"] = ["INVALID"]
    assert config.validate() is True
    
    # Test with no systems (should be invalid)
    config.systems = {}
    assert config.validate() is False