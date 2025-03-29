# app/config/star_map.py
from typing import Dict, List, Any, Optional, Tuple
from uuid import UUID

from app.config.base import BaseConfiguration

class StarSystem:
    """Represents a star system in the game."""
    
    def __init__(self, system_id: str, name: str, position: Tuple[float, float], 
                 civilization_id: Optional[str] = None, is_hub: bool = False,
                 is_dead_star: bool = False):
        self.system_id = system_id
        self.name = name
        self.position = position  # (x, y) coordinates
        self.civilization_id = civilization_id
        self.is_hub = is_hub
        self.is_dead_star = is_dead_star
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "system_id": self.system_id,
            "name": self.name,
            "position": self.position,
            "civilization_id": self.civilization_id,
            "is_hub": self.is_hub,
            "is_dead_star": self.is_dead_star
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StarSystem':
        """Create from dictionary."""
        return cls(
            system_id=data["system_id"],
            name=data["name"],
            position=tuple(data["position"]),
            civilization_id=data.get("civilization_id"),
            is_hub=data.get("is_hub", False),
            is_dead_star=data.get("is_dead_star", False)
        )

class StarMapConfig(BaseConfiguration):
    """Configuration for the star map and routes between systems."""
    
    def __init__(self, config_id: Optional[UUID] = None):
        super().__init__(config_id)
        self.systems = {}  # system_id -> StarSystem
        self.connections = {}  # system_id -> [connected system_ids]
        self._load_defaults()
    
    def _load_defaults(self):
        """Load default star map configuration."""
        defaults = self.get_defaults()
        
        # Load systems
        for system_data in defaults.get("systems", []):
            system = StarSystem.from_dict(system_data)
            self.systems[system.system_id] = system
        
        # Load connections
        self.connections = defaults.get("connections", {})
    
    def get_defaults(self) -> Dict[str, Any]:
        """Return default configuration values."""
        return {
            "systems": [
                # Civilization systems
                {
                    "system_id": "AB",
                    "name": "AB System",
                    "position": (200, 100),
                    "civilization_id": "Kyrathi Silicon Liberation",
                    "is_hub": False,
                    "is_dead_star": False
                },
                {
                    "system_id": "CD",
                    "name": "CD System",
                    "position": (300, 250),
                    "civilization_id": "Thrizoth",
                    "is_hub": False,
                    "is_dead_star": False
                },
                {
                    "system_id": "EF",
                    "name": "EF System",
                    "position": (550, 100),
                    "civilization_id": "Vasku",
                    "is_hub": False,
                    "is_dead_star": False
                },
                {
                    "system_id": "GH",
                    "name": "GH System",
                    "position": (500, 200),
                    "civilization_id": "Glacian Current",
                    "is_hub": False,
                    "is_dead_star": False
                },
                {
                    "system_id": "IJ",
                    "name": "IJ System",
                    "position": (600, 350),
                    "civilization_id": "Methane Collective",
                    "is_hub": False,
                    "is_dead_star": False
                },
                # Hub systems
                {
                    "system_id": "Alpha",
                    "name": "Alpha Hub",
                    "position": (150, 200),
                    "civilization_id": None,
                    "is_hub": True,
                    "is_dead_star": False
                },
                {
                    "system_id": "Beta",
                    "name": "Beta Hub",
                    "position": (250, 50),
                    "civilization_id": None,
                    "is_hub": True,
                    "is_dead_star": False
                },
                {
                    "system_id": "Gamma",
                    "name": "Gamma Hub",
                    "position": (550, 300),
                    "civilization_id": None,
                    "is_hub": True,
                    "is_dead_star": False
                },
                # Dead star systems
                {
                    "system_id": "D2",
                    "name": "D2 System",
                    "position": (450, 350),
                    "civilization_id": None,
                    "is_hub": False,
                    "is_dead_star": True
                },
                {
                    "system_id": "D4",
                    "name": "D4 System",
                    "position": (400, 400),
                    "civilization_id": None,
                    "is_hub": False,
                    "is_dead_star": True
                }
            ],
            "connections": {
                "AB": ["Alpha", "Beta", "CD"],
                "CD": ["AB", "D4", "Alpha"],
                "D4": ["CD", "D2"],
                "D2": ["D4", "GH", "IJ"],
                "GH": ["D2", "EF", "Gamma"],
                "EF": ["GH", "Beta"],
                "IJ": ["D2", "Gamma"],
                "Alpha": ["AB", "CD"],
                "Beta": ["AB", "EF"],
                "Gamma": ["GH", "IJ"]
            }
        }
    
    def validate(self) -> bool:
        """Validate the configuration."""
        # Debug output
        print(f"Systems: {list(self.systems.keys())}")
        print(f"Connections: {self.connections}")
        
        # Check that all systems exist
        if not self.systems:
            print("Validation failed: No systems defined")
            return False

        # Check that all systems have valid positions
        for system_id, system in self.systems.items():
            if not hasattr(system, 'position') or not isinstance(system.position, tuple) or len(system.position) != 2:
                print(f"Validation failed: Invalid position for system {system_id}: {getattr(system, 'position', None)}")
                return False
            
            # Verify position values are valid numbers
            if not all(isinstance(coord, (int, float)) for coord in system.position):
                print(f"Validation failed: Position coordinates for system {system_id} are not numbers: {system.position}")
                return False
        
        # Check that all connections reference valid systems
        for system_id, connected_ids in self.connections.items():
            if system_id not in self.systems:
                print(f"Validation failed: Connection from non-existent system {system_id}")
                return False
            for connected_id in connected_ids:
                if connected_id not in self.systems:
                    print(f"Validation failed: System {system_id} connects to non-existent system {connected_id}")
                    return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        data = super().to_dict()
        data.update({
            "systems": [system.to_dict() for system in self.systems.values()],
            "connections": self.connections
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StarMapConfig':
        """Create configuration from dictionary."""
        config = super(StarMapConfig, cls).from_dict(data)
        
        # Clear defaults
        config.systems = {}
        config.connections = {}
        
        # Load systems
        for system_data in data.get("systems", []):
            system = StarSystem.from_dict(system_data)
            config.systems[system.system_id] = system
        
        # Load connections
        config.connections = data.get("connections", {})
        
        return config
    
    def get_system(self, system_id: str) -> Optional[StarSystem]:
        """Get a star system by ID."""
        return self.systems.get(system_id)
    
    def get_hub_systems(self) -> List[StarSystem]:
        """Get all hub systems."""
        return [system for system in self.systems.values() if system.is_hub]
    
    def get_civilization_system(self, civilization_id: str) -> Optional[StarSystem]:
        """Get the home system for a civilization."""
        for system in self.systems.values():
            if system.civilization_id == civilization_id:
                return system
        return None
    
    def get_connected_systems(self, system_id: str) -> List[StarSystem]:
        """Get all systems connected to a specific system."""
        connected_ids = self.connections.get(system_id, [])
        return [self.systems[connected_id] for connected_id in connected_ids 
                if connected_id in self.systems]
    
    def find_shortest_path(self, start_id: str, end_id: str) -> List[str]:
        """Find the shortest path between two systems."""
        # Using breadth-first search for simplicity
        if start_id not in self.systems or end_id not in self.systems:
            return []
        
        visited = {start_id}
        queue = [(start_id, [start_id])]
        
        while queue:
            current_id, path = queue.pop(0)
            
            if current_id == end_id:
                return path
            
            for neighbor_id in self.connections.get(current_id, []):
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    queue.append((neighbor_id, path + [neighbor_id]))
        
        return []  # No path found
    
    def calculate_jumps(self, start_id: str, end_id: str) -> int:
        """Calculate the number of jumps between two systems."""
        path = self.find_shortest_path(start_id, end_id)
        return len(path) - 1 if path else -1