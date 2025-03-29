# app/config/trade.py
from typing import Dict, Any, Optional
from uuid import UUID

from app.config.base import BaseConfiguration

class TradeConfig(BaseConfiguration):
    """Configuration for trade rules and mechanics."""
    
    def __init__(self, config_id: Optional[UUID] = None):
        super().__init__(config_id)
        self.base_delivery_cost_percentage = 5.0  # Cost per jump as percentage
        self.min_delivery_cost_percentage = 10.0  # Minimum delivery cost
        self.max_delivery_cost_percentage = 30.0  # Maximum delivery cost
        self.hub_tax_rates = {}  # hub_id -> tax percentage
        self._load_defaults()
    
    def _load_defaults(self):
        """Load default trade configuration."""
        defaults = self.get_defaults()
        
        self.base_delivery_cost_percentage = defaults.get("base_delivery_cost_percentage", 5.0)
        self.min_delivery_cost_percentage = defaults.get("min_delivery_cost_percentage", 10.0)
        self.max_delivery_cost_percentage = defaults.get("max_delivery_cost_percentage", 30.0)
        self.hub_tax_rates = defaults.get("hub_tax_rates", {})
    
    def get_defaults(self) -> Dict[str, Any]:
        """Return default configuration values."""
        return {
            "base_delivery_cost_percentage": 5.0,
            "min_delivery_cost_percentage": 10.0,
            "max_delivery_cost_percentage": 30.0,
            "hub_tax_rates": {
                "Alpha": 0.0,
                "Beta": 0.0,
                "Gamma": 0.0
            }
        }
    
    def validate(self) -> bool:
        """Validate the configuration."""
        # Check that delivery cost percentages are valid
        if not (0 <= self.base_delivery_cost_percentage <= 100):
            return False
        if not (0 <= self.min_delivery_cost_percentage <= 100):
            return False
        if not (0 <= self.max_delivery_cost_percentage <= 100):
            return False
        if self.min_delivery_cost_percentage > self.max_delivery_cost_percentage:
            return False
        
        # Check that hub tax rates are valid
        for hub_id, rate in self.hub_tax_rates.items():
            if not (0 <= rate <= 100):
                return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        data = super().to_dict()
        data.update({
            "base_delivery_cost_percentage": self.base_delivery_cost_percentage,
            "min_delivery_cost_percentage": self.min_delivery_cost_percentage,
            "max_delivery_cost_percentage": self.max_delivery_cost_percentage,
            "hub_tax_rates": self.hub_tax_rates
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TradeConfig':
        """Create configuration from dictionary."""
        config = super(TradeConfig, cls).from_dict(data)
        
        config.base_delivery_cost_percentage = data.get("base_delivery_cost_percentage", 5.0)
        config.min_delivery_cost_percentage = data.get("min_delivery_cost_percentage", 10.0)
        config.max_delivery_cost_percentage = data.get("max_delivery_cost_percentage", 30.0)
        config.hub_tax_rates = data.get("hub_tax_rates", {})
        
        return config
    
    def calculate_delivery_cost(self, jumps: int, hub_id: str = None) -> float:
        """
        Calculate delivery cost percentage based on number of jumps.
        
        Args:
            jumps: Number of jumps
            hub_id: Optional hub ID to include hub-specific taxes
            
        Returns:
            Delivery cost as a percentage
        """
        # Base cost from jumps
        cost = jumps * self.base_delivery_cost_percentage
        
        # Apply min/max constraints
        cost = max(cost, self.min_delivery_cost_percentage)
        cost = min(cost, self.max_delivery_cost_percentage)
        
        # Add hub-specific tax if applicable
        if hub_id and hub_id in self.hub_tax_rates:
            cost += self.hub_tax_rates[hub_id]
        
        return cost