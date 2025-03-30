# tests/config/test_trade_config.py
import pytest
from unittest.mock import patch, MagicMock

from app.config.trade import TradeConfig
from app.config import initialize_configurations
from app.config.utils import get_star_map_config, get_trade_config, get_hub_distance_table
from app.services.map_service import MapService
from app.services.trade_service import TradeService
from app.schemas.enums import CivilizationName

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


@pytest.fixture
def initialized_config():
    """Initialize configurations for testing."""
    initialize_configurations()
    return {
        "star_map": get_star_map_config(),
        "trade_config": get_trade_config()
    }


class TestTradeMapIntegration:
    """Tests for trade service integration with map configuration."""
    
    def test_trade_service_uses_map_config(self, initialized_config):
        """Test that TradeService correctly uses map configuration."""
        star_map = initialized_config["star_map"]
        
        # Verify the trade service uses the correct system IDs from map config
        thrizoth_system = TradeService.get_civilization_system_id("Thrizoth")
        kyrathi_system = TradeService.get_civilization_system_id("Kyrathi")
        
        # Check that these match what's in the star map config
        for system_id, system in star_map.systems.items():
            if system.civilization_id and "Thrizoth" in system.civilization_id:
                assert thrizoth_system == system_id
            if system.civilization_id and "Kyrathi" in system.civilization_id:
                assert kyrathi_system == system_id
    
    def test_delivery_cost_uses_map_data(self, initialized_config):
        """Test that delivery cost calculation uses map data."""
        # Find systems for testing
        thrizoth_system = TradeService.get_civilization_system_id("Thrizoth")
        hub_id = "Alpha"
        
        # Get the expected number of jumps from map config
        star_map = initialized_config["star_map"]
        expected_jumps = star_map.calculate_jumps(thrizoth_system, hub_id)
        
        # Calculate expected cost based on these jumps
        trade_config = initialized_config["trade_config"]
        expected_cost = trade_config.calculate_delivery_cost(expected_jumps, hub_id)
        
        # Verify TradeService gives the same result
        actual_cost = TradeService.calculate_delivery_cost(thrizoth_system, hub_id)
        assert actual_cost == expected_cost
    
    def test_trade_route_calculation(self, initialized_config):
        """Test trade route calculation integrates map and trade data."""
        # Calculate a trade route
        route = TradeService.calculate_trade_route("Thrizoth", "Kyrathi")
        
        # Verify it uses the correct systems from map config
        thrizoth_system = TradeService.get_civilization_system_id("Thrizoth")
        kyrathi_system = TradeService.get_civilization_system_id("Kyrathi")
        
        assert route["success"] is True
        assert route["sender_system"] == thrizoth_system
        assert route["receiver_system"] == kyrathi_system
        
        # Verify the route is a valid path in the map
        star_map = initialized_config["star_map"]
        for i in range(len(route["route"]) - 1):
            system1 = route["route"][i]
            system2 = route["route"][i + 1]
            assert system2 in star_map.connections.get(system1, []) or system1 in star_map.connections.get(system2, [])
    
    def test_map_changes_affect_trade(self, initialized_config):
        """Test that changes to the map configuration affect trade calculations."""
        star_map = initialized_config["star_map"]
        
        # Get original path
        source_system = TradeService.get_civilization_system_id("Thrizoth")
        target_system = TradeService.get_civilization_system_id("Methane Collective")
        
        if not source_system or not target_system:
            pytest.skip("Required systems not found in configuration")
        
        original_path = MapService.find_shortest_path(source_system, target_system)
        original_jumps = MapService.calculate_jumps(source_system, target_system)
        original_route = TradeService.calculate_trade_route("Thrizoth", "Methane Collective")
        
        # Save original connections for restoration
        original_connections = {k: v.copy() if isinstance(v, list) else v for k, v in star_map.connections.items()}
        
        # Modify the map - add a direct connection
        if "IJ" not in star_map.connections.get(source_system, []):
            if source_system in star_map.connections:
                star_map.connections[source_system].append(target_system)
            else:
                star_map.connections[source_system] = [target_system]
                
            if target_system in star_map.connections:
                star_map.connections[target_system].append(source_system)
            else:
                star_map.connections[target_system] = [source_system]
        
        # Get new path
        modified_path = MapService.find_shortest_path(source_system, target_system)
        modified_jumps = MapService.calculate_jumps(source_system, target_system)
        modified_route = TradeService.calculate_trade_route("Thrizoth", "Methane Collective")
        
        # Check that the routes have changed
        if original_path and modified_path and len(original_path) > 1 and len(modified_path) > 1:
            # Either the path should be shorter or different
            assert (len(modified_path) < len(original_path) or 
                    original_path != modified_path)
        
        # Check that the trade routes reflect the map changes
        if original_route["success"] and modified_route["success"]:
            if "route" in original_route and "route" in modified_route:
                assert (len(modified_route["route"]) <= len(original_route["route"]) or
                        original_route["route"] != modified_route["route"])
        
        # Reset map connections
        star_map.connections = original_connections