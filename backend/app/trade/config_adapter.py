# app/trade/config_adapter.py
from typing import Dict, Tuple
from uuid import UUID
from app.config.utils import get_hub_distance_table, calculate_delivery_cost
from app.config import get_config_manager
from app.config.star_map import StarMapConfig

def get_optimal_hub_for_trade(sender_civ_id: str, receiver_civ_id: str) -> Tuple[str, float]:
    """
    Find the hub with the lowest combined delivery cost for a trade.
    
    Args:
        sender_civ_id: The sending civilization's ID (name, not UUID)
        receiver_civ_id: The receiving civilization's ID (name, not UUID)
        
    Returns:
        Tuple of (hub_id, total_cost_percentage)
    """
    # Get the hub distance table
    hub_table = get_hub_distance_table()
    
    best_hub = None
    best_cost = float('inf')
    
    # Check each hub
    for hub_id in ["Alpha", "Beta", "Gamma"]:
        sender_jumps, sender_cost = hub_table.get(sender_civ_id, {}).get(hub_id, (999, 100.0))
        receiver_jumps, receiver_cost = hub_table.get(receiver_civ_id, {}).get(hub_id, (999, 100.0))
        
        total_cost = sender_cost + receiver_cost
        
        if total_cost < best_cost:
            best_cost = total_cost
            best_hub = hub_id
    
    if best_hub is None:
        # Fallback to Alpha hub if no valid route found
        best_hub = "Alpha"
        best_cost = 100.0
    
    return (best_hub, best_cost)

# This function will be used when connecting to the actual trade system
def get_system_id_for_civilization_uuid(game_id: UUID, civ_uuid: UUID) -> str:
    """
    Get the system ID for a civilization UUID.
    
    This is a placeholder for the actual database lookup that would happen
    when integrating with the real system.
    
    Args:
        game_id: The game ID
        civ_uuid: The civilization UUID
        
    Returns:
        The system ID (e.g., "AB", "CD", etc.)
    """
    # In the real implementation, this would query the database
    # For now, return a placeholder
    return "AB"  # This would be replaced with real logic