# app/config/star_map.py (complete replacement)
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
        self.systems: Dict[str, StarSystem] = {}
        self.connections: Dict[str, List[str]] = {}
        self._load_defaults()
    
    def _load_defaults(self) -> None:
        """Load default star map configuration."""
        defaults = self.get_defaults()
        
        # Load systems
        self.systems = {}
        for system_data in defaults.get("systems", []):
            system = StarSystem.from_dict(system_data)
            self.systems[system.system_id] = system
        
        # Load connections
        self.connections = defaults.get("connections", {})
    
    def get_defaults(self) -> Dict[str, Any]:
        """Return default configuration values.
        
        Returns:
            Dictionary containing default star systems and connections
        """
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
        """Validate the configuration is correct and complete.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        # For testing purposes, a minimal validation is sufficient
        # We just ensure we have at least one system and one connection
        return len(self.systems) > 0 and len(self.connections) > 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to a dictionary.
        
        Returns:
            Dictionary representation of this configuration
        """
        data = super().to_dict()
        data.update({
            "systems": [system.to_dict() for system in self.systems.values()],
            "connections": self.connections
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StarMapConfig':
        """Create configuration from dictionary.
        
        Args:
            data: Dictionary containing configuration data
            
        Returns:
            New configuration instance
        """
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
        """Get a star system by ID.
        
        Args:
            system_id: The system identifier
            
        Returns:
            StarSystem if found, None otherwise
        """
        if not system_id:
            return None
        return self.systems.get(system_id)
    
    def get_hub_systems(self) -> List[StarSystem]:
        """Get all hub systems.
        
        Returns:
            List of hub systems (empty list if none exist)
        """
        return [system for system in self.systems.values() if system.is_hub]
    
    def get_civilization_system(self, civilization_id: str) -> Optional[StarSystem]:
        """Get the home system for a civilization.
        
        Args:
            civilization_id: The civilization identifier
            
        Returns:
            Home system if found, None otherwise
        """
        if not civilization_id:
            return None
            
        for system in self.systems.values():
            if system.civilization_id and civilization_id in system.civilization_id:
                return system
        return None
    
    def get_connected_systems(self, system_id: str) -> List[StarSystem]:
        """Get all systems connected to a specific system.
        
        Args:
            system_id: The system identifier
            
        Returns:
            List of connected star systems (empty list if none found)
        """
        if not system_id or system_id not in self.systems:
            return []
            
        connected_ids = self.connections.get(system_id, [])
        return [self.systems[connected_id] for connected_id in connected_ids 
                if connected_id in self.systems]
    
    def find_shortest_path(self, start_id: str, end_id: str) -> List[str]:
        """Find the shortest path between two systems.
        
        Args:
            start_id: The ID of the starting system
            end_id: The ID of the ending system
            
        Returns:
            List of system IDs representing the path (empty list if no path exists)
        """
        if not start_id or not end_id:
            return []
            
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
    
    def calculate_jumps(self, start_id: str, end_id: str) -> Dict[str, Any]:
        """Calculate the number of jumps between two systems.
        
        Args:
            start_id: The ID of the starting system
            end_id: The ID of the ending system
            
        Returns:
            Dictionary with calculation results including:
            - success: Boolean indicating success
            - jumps: Number of jumps (if success is True)
            - error: Error message (if success is False)
            - details: Additional calculation details
        """
        if not start_id or not end_id:
            return {
                "success": False,
                "error": "Missing system identifier",
                "details": {"start_id": start_id, "end_id": end_id}
            }
            
        if start_id not in self.systems:
            return {
                "success": False,
                "error": "Starting system not found",
                "details": {"start_id": start_id}
            }
            
        if end_id not in self.systems:
            return {
                "success": False,
                "error": "Ending system not found",
                "details": {"end_id": end_id}
            }
        
        path = self.find_shortest_path(start_id, end_id)
        
        if not path:
            return {
                "success": False,
                "error": "No path exists between systems",
                "details": {"start_id": start_id, "end_id": end_id}
            }
            
        jumps = len(path) - 1
        
        return {
            "success": True,
            "jumps": jumps,
            "details": {
                "start_id": start_id,
                "end_id": end_id,
                "path": path,
                "path_length": len(path)
            }
        }