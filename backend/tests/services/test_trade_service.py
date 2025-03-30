# tests/services/test_trade_service.py
import pytest
from unittest.mock import patch, MagicMock

from app.services.trade_service import TradeService
from app.services.map_service import MapService
from app.config.utils import get_star_map_config, get_trade_config
from app.schemas.enums import CivilizationName


class TestTradeService:
    
    @patch('app.services.trade_service.get_star_map_config')
    @patch('app.services.trade_service.get_trade_config')
    @patch('app.services.trade_service.MapService.calculate_jumps')
    def test_calculate_delivery_cost(self, mock_calculate_jumps, mock_get_trade_config, mock_get_star_map_config):
        # Setup mocks
        mock_star_map = MagicMock()
        mock_get_star_map_config.return_value = mock_star_map
        
        mock_trade_config = MagicMock()
        mock_trade_config.max_delivery_cost_percentage = 30.0
        mock_trade_config.calculate_delivery_cost.return_value = 15.0
        mock_get_trade_config.return_value = mock_trade_config
        
        # Test valid path
        mock_calculate_jumps.return_value = 2
        result = TradeService.calculate_delivery_cost("CD", "Alpha")
        
        # Verify correct methods were called
        mock_get_star_map_config.assert_called_once()
        mock_get_trade_config.assert_called_once()
        mock_calculate_jumps.assert_called_once_with("CD", "Alpha")
        mock_trade_config.calculate_delivery_cost.assert_called_once_with(2, "Alpha")
        
        # Verify result
        assert result == 15.0
        
        # Test invalid path
        mock_calculate_jumps.reset_mock()
        mock_trade_config.calculate_delivery_cost.reset_mock()
        mock_calculate_jumps.return_value = -1
        
        result = TradeService.calculate_delivery_cost("NonExistent", "Alpha")
        
        # Should return max cost for invalid path
        assert result == 30.0
        mock_trade_config.calculate_delivery_cost.assert_not_called()
    
    @patch('app.services.trade_service.get_star_map_config')
    def test_get_civilization_system_id(self, mock_get_star_map_config):
        # Setup mock
        mock_star_map = MagicMock()
        mock_system = MagicMock()
        mock_system.civilization_id = "Thrizoth"
        
        mock_star_map.systems = {
            "CD": mock_system,
            "AB": MagicMock(civilization_id="Kyrathi Silicon Liberation"),
            "GH": MagicMock(civilization_id="Glacian Current")
        }
        
        mock_get_star_map_config.return_value = mock_star_map
        
        # Test existing civilization
        result = TradeService.get_civilization_system_id("Thrizoth")
        assert result == "CD"
        
        # Test civilization in shared system
        result = TradeService.get_civilization_system_id("Silicon Liberation")
        assert result == "AB"
        
        # Test civilization not found
        result = TradeService.get_civilization_system_id("NonExistent")
        assert result is None
    
    @patch('app.services.trade_service.TradeService.get_civilization_system_id')
    @patch('app.services.trade_service.TradeService.get_optimal_hub')
    @patch('app.services.trade_service.TradeService.calculate_delivery_cost')
    @patch('app.services.trade_service.MapService.find_shortest_path')
    def test_calculate_trade_route(self, mock_find_path, mock_calc_cost, mock_get_hub, mock_get_system):
        # Setup mocks
        mock_get_system.side_effect = lambda civ: {"Thrizoth": "CD", "Kyrathi": "AB"}.get(civ)
        mock_get_hub.return_value = "Alpha"
        mock_calc_cost.side_effect = lambda sys, hub: 10.0 if sys == "CD" else 5.0
        mock_find_path.side_effect = lambda a, b: ["CD", "Alpha"] if a == "CD" else ["Alpha", "AB"]
        
        # Test successful route
        result = TradeService.calculate_trade_route("Thrizoth", "Kyrathi")
        
        assert result["success"] is True
        assert result["sender_system"] == "CD"
        assert result["receiver_system"] == "AB"
        assert result["hub"] == "Alpha"
        assert result["sender_cost_percentage"] == 10.0
        assert result["receiver_cost_percentage"] == 5.0
        assert result["total_cost_percentage"] == 15.0
        assert result["route"] == ["CD", "Alpha", "AB"]
        assert result["jumps"] == 2
        
        # Test civilization not found
        mock_get_system.side_effect = lambda civ: None if civ == "NonExistent" else "CD"
        
        result = TradeService.calculate_trade_route("NonExistent", "Thrizoth")
        
        assert result["success"] is False
        assert result["error"] == "Civilization not found"
        
        # Test no valid route
        mock_get_system.side_effect = lambda civ: "CD" if civ == "Thrizoth" else "IJ"
        mock_get_hub.return_value = None
        
        result = TradeService.calculate_trade_route("Thrizoth", "Methane Collective")
        
        assert result["success"] is False
        assert result["error"] == "No valid trade route found"
    
    def test_can_civilizations_trade(self):
        # Test allowed trades
        assert TradeService.can_civilizations_trade("Thrizoth", "Kyrathi") is True
        assert TradeService.can_civilizations_trade("Methane Collective", "Kyrathi") is True
        
        # Test communication restrictions
        assert TradeService.can_civilizations_trade("Thrizoth", "Vasku") is False
        assert TradeService.can_civilizations_trade("Glacian Current", "Methane Collective") is False
        assert TradeService.can_civilizations_trade("Silicon Liberation", "Kyrathi") is False
        
        # Test with invalid civilization names
        assert TradeService.can_civilizations_trade("Unknown", "Thrizoth") is True

    @patch('app.services.trade_service.get_star_map_config')
    @patch('app.services.trade_service.MapService.calculate_jumps')
    @patch('app.services.trade_service.get_trade_config')
    def test_get_optimal_hub(self, mock_get_trade_config, mock_calculate_jumps, mock_get_star_map_config):
        # Setup mocks
        mock_star_map = MagicMock()
        mock_hub1 = MagicMock(system_id="Alpha", is_hub=True)
        mock_hub2 = MagicMock(system_id="Beta", is_hub=True)
        
        mock_star_map.systems = {
            "Alpha": mock_hub1,
            "Beta": mock_hub2,
            "CD": MagicMock(is_hub=False),
            "IJ": MagicMock(is_hub=False)
        }
        
        mock_get_star_map_config.return_value = mock_star_map
        
        mock_trade_config = MagicMock()
        mock_trade_config.calculate_delivery_cost.side_effect = lambda jumps, hub: 10.0 if hub == "Alpha" else 5.0
        mock_get_trade_config.return_value = mock_trade_config
        
        # Configure calculate_jumps to return different values for different combinations
        def mock_jumps(src, hub):
            if src == "CD" and hub == "Alpha":
                return 1  # CD to Alpha: 1 jump
            elif src == "CD" and hub == "Beta":
                return 2  # CD to Beta: 2 jumps
            elif src == "IJ" and hub == "Alpha":
                return 3  # IJ to Alpha: 3 jumps
            elif src == "IJ" and hub == "Beta":
                return 1  # IJ to Beta: 1 jump
            return -1  # No path
        
        mock_calculate_jumps.side_effect = mock_jumps
        
        # Test optimal hub calculation - Beta should be optimal because total cost is lower
        # CD to Alpha (10.0) + IJ to Alpha (10.0) = 20.0
        # CD to Beta (5.0) + IJ to Beta (5.0) = 10.0
        result = TradeService.get_optimal_hub("CD", "IJ")
        
        assert result == "Beta"  # Beta should be optimal
        
        # Test when no path exists to any hub
        mock_calculate_jumps.side_effect = lambda src, hub: -1  # No path to any hub
        
        result = TradeService.get_optimal_hub("CD", "IJ")
        
        assert result is None