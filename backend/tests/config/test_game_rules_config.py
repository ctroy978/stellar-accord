# tests/config/test_game_rules_config.py
import pytest
from uuid import uuid4
from app.config.game_rules import GameRulesConfig

def test_game_rules_initialization():
    """Test that the game rules configuration initializes correctly."""
    config = GameRulesConfig(config_id=uuid4())
    
    # Verify round structure
    assert "main" in config.round_structure
    assert "cleanup" in config.round_structure
    assert len(config.round_structure) == 2
    
    # Verify phase durations
    assert config.phase_durations["main"] == 15
    assert config.phase_durations["cleanup"] == 2
    
    # Verify communication restrictions
    assert "Thrizoth" in config.communication_restrictions
    assert "Vasku" in config.communication_restrictions["Thrizoth"]
    
    # Verify law settings
    assert config.law_duration == 3
    assert config.max_active_laws == 6
    
    # Verify trading rules
    assert "base_delivery_cost_percentage" in config.trading_rules
    
    # Verify intelligence operations
    assert "universal_operations" in config.intelligence_operation_rules

def test_game_rules_serialization():
    """Test that the game rules config can be serialized and deserialized."""
    original = GameRulesConfig(config_id=uuid4())
    
    # Modify some values for testing
    original.law_duration = 4
    original.max_active_laws = 8
    original.trading_rules["base_delivery_cost_percentage"] = 7.5
    
    # Serialize
    data = original.to_dict()
    
    # Deserialize
    recreated = GameRulesConfig.from_dict(data)
    
    # Verify values match
    assert recreated.law_duration == 4
    assert recreated.max_active_laws == 8
    assert recreated.trading_rules["base_delivery_cost_percentage"] == 7.5
    
    # Verify other values were preserved
    assert len(recreated.round_structure) == len(original.round_structure)
    assert recreated.communication_restrictions == original.communication_restrictions

def test_can_civilizations_communicate():
    """Test the communication restriction checking."""
    config = GameRulesConfig()
    
    # Test civilizations that can't communicate
    assert config.can_civilizations_communicate("Thrizoth", "Vasku") is False
    assert config.can_civilizations_communicate("Methane Collective", "Glacian Current") is False
    
    # Test civilizations that can communicate
    assert config.can_civilizations_communicate("Thrizoth", "Methane Collective") is True
    assert config.can_civilizations_communicate("Kyrathi", "Vasku") is True
    
    # Test with civilization not in restrictions
    assert config.can_civilizations_communicate("Unknown Civ", "Thrizoth") is True

def test_get_phase_duration():
    """Test retrieving phase durations."""
    config = GameRulesConfig()
    
    assert config.get_phase_duration("main") == 15
    assert config.get_phase_duration("cleanup") == 2
    
    # Test non-existent phase
    assert config.get_phase_duration("nonexistent") == 0

def test_get_next_phase():
    """Test getting the next phase in sequence."""
    config = GameRulesConfig()
    
    assert config.get_next_phase("main") == "cleanup"
    assert config.get_next_phase("cleanup") == "main"
    
    # Test invalid phase
    assert config.get_next_phase("nonexistent") == "main"

def test_is_last_phase_in_round():
    """Test checking if a phase is the last in a round."""
    config = GameRulesConfig()
    
    assert config.is_last_phase_in_round("main") is False
    assert config.is_last_phase_in_round("cleanup") is True
    
    # Test invalid phase
    assert config.is_last_phase_in_round("nonexistent") is False

def test_calculate_intelligence_success_rate():
    """Test calculating intelligence operation success rates."""
    config = GameRulesConfig()
    
    # Test basic operation with no additional resources
    success_rate = config.calculate_intelligence_success_rate(
        "Basic Resource Monitoring", {}
    )
    assert success_rate == 60.0  # Base rate, no improvement
    
    # Test with additional resources - below diminishing returns threshold
    success_rate = config.calculate_intelligence_success_rate(
        "Basic Resource Monitoring", 
        {"Quantum Particles": 100, "Carbon Matrices": 100}
    )
    # 100/5 = 20 points for each resource, total 40 points
    # But capped at max_additional_success_rate (30)
    assert success_rate == 90.0  # 60 + 30
    
    # Test operation that doesn't exist
    success_rate = config.calculate_intelligence_success_rate(
        "Nonexistent Operation", {}
    )
    assert success_rate == 0.0

def test_validate():
    """Test configuration validation."""
    config = GameRulesConfig()
    
    # Valid configuration
    assert config.validate() is True
    
    # Invalid round structure
    original_round_structure = config.round_structure
    config.round_structure = ["main"]  # Missing cleanup phase
    assert config.validate() is False
    config.round_structure = original_round_structure
    
    # Invalid phase duration
    original_phase_durations = config.phase_durations
    config.phase_durations = {"main": 15}  # Missing cleanup duration
    assert config.validate() is False
    config.phase_durations = original_phase_durations
    
    # Invalid law duration
    config.law_duration = 0
    assert config.validate() is False
    config.law_duration = 3
    
    # Invalid max active laws
    config.max_active_laws = -1
    assert config.validate() is False
    config.max_active_laws = 6
    
    # Invalid trading rule percentages
    original_trading_rules = config.trading_rules.copy()
    config.trading_rules["base_delivery_cost_percentage"] = 150  # Above 100%
    assert config.validate() is False
    config.trading_rules = original_trading_rules
    
    # Min cost exceeds max cost
    config.trading_rules["min_delivery_cost_percentage"] = 40
    config.trading_rules["max_delivery_cost_percentage"] = 30
    assert config.validate() is False