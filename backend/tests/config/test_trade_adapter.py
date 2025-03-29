# tests/config/test_trade_adapter.py
import pytest
from uuid import uuid4
from app.trade.config_adapter import get_optimal_hub_for_trade

class TestTradeAdapter:
    def test_optimal_hub_calculation(self):
        """Test calculation of optimal hub for trade."""
        # Test with existing civilizations
        hub, cost = get_optimal_hub_for_trade("Thrizoth", "Methane Collective")
        
        # Verify results
        assert hub in ["Alpha", "Beta", "Gamma"]
        assert isinstance(cost, float)
        assert 0 <= cost <= 100.0
    
    def test_invalid_civilizations(self):
        """Test with invalid civilization names."""
        # Should not raise exceptions, but return a fallback
        hub, cost = get_optimal_hub_for_trade("NonExistent1", "NonExistent2")
        assert hub in ["Alpha", "Beta", "Gamma"]