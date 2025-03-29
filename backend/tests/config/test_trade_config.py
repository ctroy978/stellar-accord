# tests/config/test_trade_config.py
import pytest
from app.config.trade import TradeConfig

class TestTradeConfig:
    def test_init_with_defaults(self):
        """Test initialization with defaults."""
        config = TradeConfig()
        # Verify the configuration loads, without asserting specific values
        assert hasattr(config, "base_delivery_cost_percentage")
        assert hasattr(config, "min_delivery_cost_percentage")
        assert hasattr(config, "max_delivery_cost_percentage")
    
    def test_calculate_delivery_cost(self):
        """Test delivery cost calculation logic, not specific values."""
        config = TradeConfig()
        
        # Save the configuration values for calculation
        base_cost = config.base_delivery_cost_percentage
        min_cost = config.min_delivery_cost_percentage
        max_cost = config.max_delivery_cost_percentage
        
        # Basic calculation
        jumps = 3
        expected_basic_cost = jumps * base_cost
        if expected_basic_cost < min_cost:
            expected_basic_cost = min_cost
        if expected_basic_cost > max_cost:
            expected_basic_cost = max_cost
            
        actual_cost = config.calculate_delivery_cost(jumps)
        assert actual_cost == expected_basic_cost
        
        # Minimum cost threshold
        jumps = 1
        expected_min_cost = jumps * base_cost
        if expected_min_cost < min_cost:
            expected_min_cost = min_cost
            
        actual_min_cost = config.calculate_delivery_cost(jumps)
        assert actual_min_cost == expected_min_cost
        
        # Maximum cost threshold
        jumps = 100  # Intentionally high to hit max
        expected_max_cost = min(jumps * base_cost, max_cost)
        
        actual_max_cost = config.calculate_delivery_cost(jumps)
        assert actual_max_cost == expected_max_cost
        
        # With hub tax
        hub_id = "Alpha"
        tax_rate = 5.0
        config.hub_tax_rates = {hub_id: tax_rate}
        
        jumps = 3
        expected_tax_cost = jumps * base_cost + tax_rate
        if expected_tax_cost < min_cost:
            expected_tax_cost = min_cost
        if expected_tax_cost > max_cost:
            expected_tax_cost = max_cost
            
        actual_tax_cost = config.calculate_delivery_cost(jumps, hub_id)
        assert actual_tax_cost == expected_tax_cost
    
    def test_validate(self):
        """Test configuration validation."""
        config = TradeConfig()
        assert config.validate() is True
        
        # Invalid percentages
        original_base = config.base_delivery_cost_percentage
        config.base_delivery_cost_percentage = -5.0
        assert config.validate() is False
        
        # Restore and test min > max
        config.base_delivery_cost_percentage = original_base
        original_min = config.min_delivery_cost_percentage
        original_max = config.max_delivery_cost_percentage
        
        config.min_delivery_cost_percentage = 40.0
        config.max_delivery_cost_percentage = 30.0
        assert config.validate() is False  # Min > Max
        
        # Restore for other tests
        config.min_delivery_cost_percentage = original_min
        config.max_delivery_cost_percentage = original_max