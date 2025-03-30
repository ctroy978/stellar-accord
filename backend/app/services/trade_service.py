# app/services/trade_service.py
"""
Trade Service Module

This module provides functionality for calculating trade routes and costs
in the Stellar Accord game. It integrates with the map configuration system
to ensure that trade calculations are based on the current spatial layout
of the game universe.

Key features:
- Delivery cost calculation based on stellar distances
- Optimal trade route planning
- Hub selection optimization
- Communication restriction enforcement
"""

from typing import Dict, Tuple, Optional, List
from app.config.utils import get_star_map_config, get_trade_config, get_hub_distance_table
from app.services.map_service import MapService
from app.schemas.enums import CivilizationName

class TradeService:
    """
    Service for trade-related operations using the configuration system.
    
    This service relies on the map configuration to calculate spatial
    distances, find optimal routes, and determine costs for trades.
    It does not contain any hard-coded map data, instead retrieving
    all spatial information from the StarMapConfig class.
    """
    
    @staticmethod
    def calculate_delivery_cost(civ_system_id: str, hub_id: str) -> float:
        """
        Calculate delivery cost between a civilization's system and a hub.
        
        This method uses the MapService to find the number of jumps between
        systems, then applies the trade configuration's cost formulas.
        
        Args:
            civ_system_id: The system ID of the civilization
            hub_id: The ID of the hub
            
        Returns:
            Delivery cost as a percentage
        """
        # Get configurations
        star_map = get_star_map_config()
        trade_config = get_trade_config()
        
        # Calculate jumps using map service
        jumps = MapService.calculate_jumps(civ_system_id, hub_id)
        
        if jumps < 0:
            # No valid path
            return trade_config.max_delivery_cost_percentage
        
        # Apply trade rules to the spatial data
        return trade_config.calculate_delivery_cost(jumps, hub_id)
    
    @staticmethod
    def get_hub_distance_table() -> Dict[str, Dict[str, Tuple[int, float]]]:
        """
        Get a table of jumps and delivery costs for all civilizations and hubs.
        
        This method uses both map and trade configuration data to build a
        comprehensive distance and cost table. It's useful for UI displays
        and for helping players make informed trade decisions.
        
        Returns a dictionary mapping:
        civilization_id -> {
            hub_id -> (jumps, cost_percentage)
        }
        """
        return get_hub_distance_table()
    
    @staticmethod
    def get_civilization_system_id(civilization_name: str) -> Optional[str]:
        """
        Get the system ID for a civilization.
        
        This method uses the map configuration to find which star system
        belongs to a given civilization.
        
        Args:
            civilization_name: The name of the civilization
            
        Returns:
            The system ID or None if not found
        """
        star_map = get_star_map_config()
        
        for system_id, system in star_map.systems.items():
            if system.civilization_id and civilization_name in system.civilization_id:
                return system_id
        
        return None
    
    @staticmethod
    def get_optimal_hub(sender_system_id: str, receiver_system_id: str) -> Optional[str]:
        """
        Determine the optimal hub for a trade between two systems.
        
        This method uses both map and trade configuration data to find
        the hub that provides the lowest total delivery cost for both
        the sender and receiver.
        
        Args:
            sender_system_id: The system ID of the sender
            receiver_system_id: The system ID of the receiver
            
        Returns:
            The ID of the optimal hub or None if not found
        """
        star_map = get_star_map_config()
        trade_config = get_trade_config()
        
        # Get all hubs
        hubs = [system.system_id for system in star_map.systems.values() if system.is_hub]
        
        if not hubs:
            return None
        
        # Calculate total cost through each hub
        lowest_cost = float('inf')
        best_hub = None
        
        for hub_id in hubs:
            # Calculate sender to hub cost
            sender_jumps = MapService.calculate_jumps(sender_system_id, hub_id)
            if sender_jumps < 0:
                continue  # No path to this hub
                
            sender_cost = trade_config.calculate_delivery_cost(sender_jumps, hub_id)
            
            # Calculate receiver to hub cost
            receiver_jumps = MapService.calculate_jumps(receiver_system_id, hub_id)
            if receiver_jumps < 0:
                continue  # No path to this hub
                
            receiver_cost = trade_config.calculate_delivery_cost(receiver_jumps, hub_id)
            
            # Total cost
            total_cost = sender_cost + receiver_cost
            
            if total_cost < lowest_cost:
                lowest_cost = total_cost
                best_hub = hub_id
        
        return best_hub
    
    @staticmethod
    def calculate_trade_route(sender_civ: str, receiver_civ: str) -> Dict:
        """
        Calculate the optimal trade route between two civilizations.
        
        This method combines multiple map-related operations:
        1. Finding the civilizations' star systems from the map config
        2. Identifying the optimal hub for the trade
        3. Calculating delivery costs based on spatial distances
        4. Finding the shortest path using the map configuration
        
        Args:
            sender_civ: The name of the sending civilization
            receiver_civ: The name of the receiving civilization
            
        Returns:
            Dictionary with route information
        """
        # Get system IDs
        sender_system_id = TradeService.get_civilization_system_id(sender_civ)
        receiver_system_id = TradeService.get_civilization_system_id(receiver_civ)
        
        if not sender_system_id or not receiver_system_id:
            return {
                "success": False,
                "error": "Civilization not found"
            }
        
        # Get optimal hub
        hub_id = TradeService.get_optimal_hub(sender_system_id, receiver_system_id)
        
        if not hub_id:
            return {
                "success": False,
                "error": "No valid trade route found"
            }
        
        # Calculate costs
        sender_cost = TradeService.calculate_delivery_cost(sender_system_id, hub_id)
        receiver_cost = TradeService.calculate_delivery_cost(receiver_system_id, hub_id)
        
        # Calculate path
        sender_to_hub = MapService.find_shortest_path(sender_system_id, hub_id)
        hub_to_receiver = MapService.find_shortest_path(hub_id, receiver_system_id)
        
        # Build full route (remove duplicate hub)
        full_route = sender_to_hub + hub_to_receiver[1:]
        
        return {
            "success": True,
            "sender_system": sender_system_id,
            "receiver_system": receiver_system_id,
            "hub": hub_id,
            "sender_cost_percentage": sender_cost,
            "receiver_cost_percentage": receiver_cost,
            "total_cost_percentage": sender_cost + receiver_cost,
            "route": full_route,
            "jumps": len(full_route) - 1
        }
    
    @staticmethod
    def can_civilizations_trade(civ1: str, civ2: str) -> bool:
        """
        Check if two civilizations can directly trade with each other.
        
        This checks if they have communication restrictions defined in the game rules.
        While not directly using the map configuration, this method complements
        the trade route calculation by enforcing diplomatic restrictions.
        
        Args:
            civ1: The name of the first civilization
            civ2: The name of the second civilization
            
        Returns:
            True if they can trade directly, False otherwise
        """
        # Check known communication restrictions
        restrictions = {
            CivilizationName.THRIZOTH: [CivilizationName.VASKU],
            CivilizationName.VASKU: [CivilizationName.THRIZOTH],
            CivilizationName.GLACIAN_CURRENT: [CivilizationName.METHANE_COLLECTIVE],
            CivilizationName.METHANE_COLLECTIVE: [CivilizationName.GLACIAN_CURRENT],
            CivilizationName.SILICON_LIBERATION: [CivilizationName.KYRATHI],
            CivilizationName.KYRATHI: [CivilizationName.SILICON_LIBERATION]
        }
        
        try:
            civ1_enum = CivilizationName(civ1)
            civ2_enum = CivilizationName(civ2)
            
            if civ1_enum in restrictions and civ2_enum in restrictions[civ1_enum]:
                return False
            
            if civ2_enum in restrictions and civ1_enum in restrictions[civ2_enum]:
                return False
                
            return True
            
        except ValueError:
            # If names aren't valid enums, default to allowing trade
            return True