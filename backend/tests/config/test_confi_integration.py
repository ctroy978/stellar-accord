# tests/config/test_config_integration.py
import pytest
from app.config import get_config_manager
from app.config.star_map import StarMapConfig
from app.config.trade import TradeConfig
from app.services.map_service import MapService
from app.services.trade_service import TradeService

class TestConfigurationIntegration:
    def test_config_system_initialization(self):
        """Test that configuration system initializes correctly."""
        config_manager = get_config_manager()
        
        star_map = config_manager.get_config("star_map")
        assert isinstance(star_map, StarMapConfig)
        
        trade_config = config_manager.get_config("trade")
        assert isinstance(trade_config, TradeConfig)
    
    def test_map_service_integration(self):
        """Test that map service correctly uses configuration."""
        # Get path between systems
        path = MapService.find_shortest_path("AB", "CD")
        assert path[0] == "AB"
        assert path[-1] == "CD"
        
        # Calculate jumps
        jumps = MapService.calculate_jumps("AB", "CD")
        assert jumps == 1
    
    def test_trade_service_integration(self):
        """Test that trade service correctly uses configuration."""
        # Calculate delivery cost
        cost = TradeService.calculate_delivery_cost("AB", "Alpha")
        assert cost == 10.0  # Should be at least minimum cost
        
        # Modify trade config and test again
        config_manager = get_config_manager()
        trade_config = config_manager.get_config("trade")
        
        original_base_cost = trade_config.base_delivery_cost_percentage
        trade_config.base_delivery_cost_percentage = 20.0
        
        # Recalculate with modified config
        cost = TradeService.calculate_delivery_cost("AB", "Alpha")
        assert cost == 20.0  # 1 jump * 20% = 20%
        
        # Reset for other tests
        trade_config.base_delivery_cost_percentage = original_base_cost