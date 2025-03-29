# tests/config/test_trade_service_integration.py
import pytest
from app.config import get_config_manager
from app.services.map_service import MapService
from app.services.trade_service import TradeService

class TestTradeServiceIntegration:
    def test_delivery_cost_calculation(self):
        """Test delivery cost calculation using current configuration."""
        # Get the current configurations
        config_manager = get_config_manager()
        star_map = config_manager.get_config("star_map")
        trade_config = config_manager.get_config("trade")
        
        # Calculate expected cost based on current configuration
        civ_system_id = "AB"
        hub_id = "Alpha"
        
        # Get the number of jumps from star map
        jumps = star_map.calculate_jumps(civ_system_id, hub_id)
        
        # Calculate expected cost based on trade rules
        expected_cost = jumps * trade_config.base_delivery_cost_percentage
        if expected_cost < trade_config.min_delivery_cost_percentage:
            expected_cost = trade_config.min_delivery_cost_percentage
        if expected_cost > trade_config.max_delivery_cost_percentage:
            expected_cost = trade_config.max_delivery_cost_percentage
            
        # Add hub tax if applicable
        if hub_id in trade_config.hub_tax_rates:
            expected_cost += trade_config.hub_tax_rates[hub_id]
        
        # Get the actual cost from the service
        actual_cost = TradeService.calculate_delivery_cost(civ_system_id, hub_id)
        
        # Compare calculated and service-provided values
        assert actual_cost == expected_cost
        
    def test_config_modification_effect(self):
        """Test that configuration changes affect calculation results."""
        # Get initial configuration
        config_manager = get_config_manager()
        trade_config = config_manager.get_config("trade")
        
        # Save original values to restore later
        original_base_cost = trade_config.base_delivery_cost_percentage
        
        try:
            # Modify the configuration
            trade_config.base_delivery_cost_percentage = original_base_cost * 2
            
            # Pick a known route
            civ_system_id = "CD"
            hub_id = "Alpha"
            
            # Get jumps from map service
            jumps = MapService.calculate_jumps(civ_system_id, hub_id)
            
            # Calculate expected cost with modified configuration
            expected_cost = jumps * trade_config.base_delivery_cost_percentage
            if expected_cost < trade_config.min_delivery_cost_percentage:
                expected_cost = trade_config.min_delivery_cost_percentage
            if expected_cost > trade_config.max_delivery_cost_percentage:
                expected_cost = trade_config.max_delivery_cost_percentage
            
            # Get the actual cost from the service
            actual_cost = TradeService.calculate_delivery_cost(civ_system_id, hub_id)
            
            # Compare calculated and service-provided values
            assert actual_cost == expected_cost
            
        finally:
            # Restore original configuration for other tests
            trade_config.base_delivery_cost_percentage = original_base_cost