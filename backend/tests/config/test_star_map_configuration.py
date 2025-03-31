# tests/config/test_star_map_configuration.py (complete replacement)
import pytest
from app.config.star_map import StarMapConfig, StarSystem

class TestStarMapConfig:
    def test_initialization(self):
        """Test initialization with defaults."""
        config = StarMapConfig()
        
        # Check systems were initialized
        assert config.systems is not None
        assert isinstance(config.systems, dict)
        assert len(config.systems) > 0
        
        # Check connections were initialized
        assert config.connections is not None
        assert isinstance(config.connections, dict)
        assert len(config.connections) > 0
        
        # Check validation passes
        assert config.validate() is True
    
    def test_get_system(self):
        """Test getting a system by ID."""
        config = StarMapConfig()
        
        # Test with valid system ID
        system = config.get_system("AB")
        assert system is not None
        assert system.system_id == "AB"
        assert isinstance(system.position, tuple)
        
        # Test with invalid system ID
        system = config.get_system("NonExistentSystem")
        assert system is None
        
        # Test with None
        system = config.get_system(None)
        assert system is None
    
    def test_get_hub_systems(self):
        """Test getting all hub systems."""
        config = StarMapConfig()
        
        hubs = config.get_hub_systems()
        assert isinstance(hubs, list)
        assert len(hubs) > 0
        
        # Verify all returned systems are hubs
        for hub in hubs:
            assert hub.is_hub is True
    
    def test_find_shortest_path(self):
        """Test finding the shortest path between systems."""
        config = StarMapConfig()
        
        # Test with valid systems
        path = config.find_shortest_path("AB", "CD")
        assert isinstance(path, list)
        assert len(path) > 0
        assert path[0] == "AB"
        assert path[-1] == "CD"
        
        # Test with same start and end
        path = config.find_shortest_path("AB", "AB")
        assert isinstance(path, list)
        assert len(path) == 1
        assert path[0] == "AB"
        
        # Test with nonexistent system
        path = config.find_shortest_path("AB", "NonExistentSystem")
        assert isinstance(path, list)
        assert len(path) == 0
        
        # Test with None values
        path = config.find_shortest_path(None, "AB")
        assert isinstance(path, list)
        assert len(path) == 0
    
    def test_calculate_jumps(self):
        """Test calculating jumps between systems."""
        config = StarMapConfig()
        
        # Test with valid systems
        result = config.calculate_jumps("AB", "CD")
        assert isinstance(result, dict)
        assert result["success"] is True
        assert "jumps" in result
        assert isinstance(result["jumps"], int)
        assert result["jumps"] > 0
        
        # Test with same start and end
        result = config.calculate_jumps("AB", "AB")
        assert result["success"] is True
        assert result["jumps"] == 0
        
        # Test with nonexistent system
        result = config.calculate_jumps("AB", "NonExistentSystem")
        assert result["success"] is False
        assert "error" in result
        
        # Test with None values
        result = config.calculate_jumps(None, "AB")
        assert result["success"] is False
        assert "error" in result
    
    def test_serialization(self):
        """Test serialization to/from dictionary."""
        config = StarMapConfig()
        
        # Convert to dictionary
        data = config.to_dict()
        assert isinstance(data, dict)
        assert "systems" in data
        assert "connections" in data
        
        # Create new config from dictionary
        new_config = StarMapConfig.from_dict(data)
        assert isinstance(new_config, StarMapConfig)
        
        # Verify systems were loaded
        assert len(new_config.systems) == len(config.systems)
        
        # Verify connections were loaded
        assert len(new_config.connections) == len(config.connections)