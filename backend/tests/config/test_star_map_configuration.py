# tests/config/test_star_map_config.py
import pytest
from app.config.star_map import StarMapConfig, StarSystem

class TestStarMapConfig:
    def test_init_with_defaults(self):
        """Test initialization with defaults."""
        config = StarMapConfig()
        assert len(config.systems) > 0
        assert len(config.connections) > 0
    
    def test_get_system(self):
        """Test getting a system by ID."""
        config = StarMapConfig()
        system = config.get_system("AB")
        assert system is not None
        assert system.system_id == "AB"
    
    def test_find_shortest_path(self):
        """Test path finding between systems."""
        config = StarMapConfig()
        
        # Direct connection
        path = config.find_shortest_path("AB", "CD")
        assert path == ["AB", "CD"]
        
        # Multi-jump path
        path = config.find_shortest_path("AB", "IJ")
        assert path[0] == "AB"
        assert path[-1] == "IJ"
        
        # No path
        config.connections = {}  # Remove all connections
        path = config.find_shortest_path("AB", "CD")
        assert path == []
    
    def test_calculate_jumps(self):
        """Test jump calculation."""
        config = StarMapConfig()
        
        # Direct connection
        jumps = config.calculate_jumps("AB", "CD")
        assert jumps == 1
        
        # No path
        config.connections = {}  # Remove all connections
        jumps = config.calculate_jumps("AB", "CD")
        assert jumps == -1
    
    def test_to_dict_and_from_dict(self):
        """Test serialization and deserialization."""
        config = StarMapConfig()
        data = config.to_dict()
        
        new_config = StarMapConfig.from_dict(data)
        assert len(new_config.systems) == len(config.systems)
        assert len(new_config.connections) == len(config.connections)