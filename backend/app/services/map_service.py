# app/services/map_service.py
"""
Map Service Module

This module provides functionality for map-related operations in the Stellar Accord game.
It acts as a bridge between the application and the map configuration system,
providing methods for spatial calculations, path finding, and related operations.

All spatial data comes from the configuration system, ensuring that 
any changes to the map layout are immediately reflected in all operations.
"""

from typing import List
from app.config import get_config_manager
from app.config.utils import get_star_map_config  # Add this import

class MapService:
    """
    Service for map-related operations using the configuration system.
    
    This service provides methods for finding paths, calculating distances,
    and other spatial operations. All methods use the map configuration
    as the source of truth for spatial data, avoiding any hard-coded
    map information.
    """
    
    @staticmethod
    def find_shortest_path(start_id: str, end_id: str) -> List[str]:
        """
        Find the shortest path between two systems.
        
        This method uses the star map configuration to find the shortest
        path between two star systems, using a breadth-first search algorithm.
        
        Args:
            start_id: The ID of the starting system
            end_id: The ID of the ending system
            
        Returns:
            A list of system IDs representing the path, or an empty list if no path exists
        """
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
        """
        Calculate the number of jumps between two systems.
        
        This method uses the star map configuration to determine the
        number of jumps required to travel between two star systems.
        The result is used for calculating trade costs and other
        distance-dependent operations.
        
        Args:
            start_id: The ID of the starting system
            end_id: The ID of the ending system
            
        Returns:
            The number of jumps, or -1 if no path exists
        """
        config_manager = get_config_manager()
        star_map = config_manager.get_config("star_map")
        
        # Handle None configuration
        if star_map is None:
            star_map = get_star_map_config()
            
        # Default to -1 if still None
        if star_map is None:
            return -1
            
        return star_map.calculate_jumps(start_id, end_id)