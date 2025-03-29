# app/services/map_service.py
from typing import List
from app.config import get_config_manager
from app.config.utils import get_star_map_config  # Add this import

class MapService:
    """Service for map-related operations using the configuration system."""
    
    @staticmethod
    def find_shortest_path(start_id: str, end_id: str) -> List[str]:
        """Find the shortest path between two systems."""
        config_manager = get_config_manager()
        star_map = config_manager.get_config("star_map")
        
        # Handle None configuration
        if star_map is None:
            star_map = get_star_map_config()
            
        # Default to empty list if still None
        if star_map is None:
            return []
            
        return star_map.find_shortest_path(start_id, end_id)
    
    @staticmethod
    def calculate_jumps(start_id: str, end_id: str) -> int:
        """Calculate the number of jumps between two systems."""
        config_manager = get_config_manager()
        star_map = config_manager.get_config("star_map")
        
        # Handle None configuration
        if star_map is None:
            star_map = get_star_map_config()
            
        # Default to -1 if still None
        if star_map is None:
            return -1
            
        return star_map.calculate_jumps(start_id, end_id)