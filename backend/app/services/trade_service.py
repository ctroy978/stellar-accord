# app/services/trade_service.py
from app.config import get_config_manager
from app.services.map_service import MapService

class TradeService:
    """Service for trade-related operations using the configuration system."""
    
    @staticmethod
    def calculate_delivery_cost(civ_system_id: str, hub_id: str) -> float:
        """Calculate delivery cost between a civilization's system and a hub."""
        config_manager = get_config_manager()
        trade_config = config_manager.get_config("trade")
        
        # Calculate jumps using map service
        jumps = MapService.calculate_jumps(civ_system_id, hub_id)
        
        if jumps < 0:
            # No valid path
            return trade_config.max_delivery_cost_percentage
        
        # Apply trade rules to the spatial data
        return trade_config.calculate_delivery_cost(jumps, hub_id)