# tests/services/test_map_service.py
import pytest
from unittest.mock import patch, MagicMock
from app.services.map_service import MapService

class TestMapService:
    def test_get_shortest_path_success(self):
        """Test successful path finding."""
        result = MapService.get_shortest_path("AB", "CD")

        assert isinstance(result, dict)
        assert "success" in result
        assert result["success"] is True
        assert "path" in result
        assert isinstance(result["path"], list)
        assert len(result["path"]) > 0
        assert "details" in result
        assert "jumps" in result["details"]

    def test_get_shortest_path_no_path(self):
        """Test when no path exists."""
        # We'll use a mock to simulate no path
        with patch("app.config.utils.get_star_map_config") as mock_get_config:
            mock_config = MagicMock()
            mock_system = MagicMock()

            # Mock returns for system lookups
            mock_config.get_system.return_value = mock_system

            # Mock no path found
            mock_config.find_shortest_path.return_value = []

            mock_get_config.return_value = mock_config

            result = MapService.get_shortest_path("AB", "XYZ")

            assert isinstance(result, dict)
            assert "success" in result
            assert result["success"] is False
            assert "error" in result

    def test_get_shortest_path_system_not_found(self):
        """Test when system is not found."""
        # We'll use a mock to simulate missing system
        with patch("app.config.utils.get_star_map_config") as mock_get_config:
            mock_config = MagicMock()

            # Mock returns for system lookups
            mock_config.get_system.return_value = None

            mock_get_config.return_value = mock_config

            result = MapService.get_shortest_path("NonExistent", "CD")

            assert isinstance(result, dict)
            assert "success" in result
            assert result["success"] is False
            assert "error" in result
            assert "Starting system not found" in result["error"]


    def test_calculate_route_distance_success(self):
        """Test successful route distance calculation."""
        # We'll use a mock to control the connections
        with patch("app.config.utils.get_star_map_config") as mock_get_config:
            # Create a mock config object with the connections property
            mock_config = MagicMock()
            mock_system = MagicMock()

            # Mock returns for system lookups
            mock_config.get_system.return_value = mock_system

            # Create a connections dictionary
            connections = {
                "A": ["B"],
                "B": ["C"],
                "C": ["D"]
            }

            # Attach the connections dictionary to the mock config
            mock_config.connections = connections

            mock_get_config.return_value = mock_config

            result = MapService.calculate_route_distance(["A", "B", "C", "D"])

            assert isinstance(result, dict)
            assert "success" in result
            assert result["success"] is True

    def test_calculate_route_distance_invalid_route(self):
        """Test route distance with invalid route."""
        # We'll use a mock to control the connections
        with patch("app.config.utils.get_star_map_config") as mock_get_config:
            mock_config = MagicMock()
            mock_system = MagicMock()

            # Mock returns for system lookups
            mock_config.get_system.return_value = mock_system

            # Set up connections dictionary
            mock_config.connections = {
                "A": ["B"],
                "B": [],  # B is not connected to C
                "C": ["D"]
            }

            mock_get_config.return_value = mock_config

            result = MapService.calculate_route_distance(["A", "B", "C", "D"])

            assert isinstance(result, dict)
            assert "success" in result
            assert result["success"] is False
            assert "error" in result
            assert "Invalid route" in result["error"]

    def test_get_civilization_location_success(self):
        """Test successfully getting civilization location."""
        result = MapService.get_civilization_location("Thrizoth")

        assert isinstance(result, dict)
        assert "success" in result
        assert result["success"] is True
        assert "system" in result
        assert "system_id" in result["system"]
        assert "connected_systems" in result["details"]

    def test_get_civilization_location_not_found(self):
        """Test getting location for nonexistent civilization."""
        # We'll use a mock to simulate missing civilization
        with patch("app.config.utils.get_star_map_config") as mock_get_config:
            mock_config = MagicMock()

            # Mock no civilization found
            mock_config.get_civilization_system.return_value = None

            mock_get_config.return_value = mock_config

            result = MapService.get_civilization_location("NonExistentCiv")

            assert isinstance(result, dict)
            assert "success" in result
            assert result["success"] is False
            assert "error" in result
            assert "Civilization not found" in result["error"]