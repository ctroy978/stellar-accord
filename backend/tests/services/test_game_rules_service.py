# tests/services/test_game_rules_service.py
import pytest
from app.services.game_rules_service import GameRulesService

def test_get_round_structure():
    """Test retrieving the round structure."""
    round_structure = GameRulesService.get_round_structure()
    
    # Check all expected phases are present
    assert "main" in round_structure
    assert "cleanup" in round_structure
    
    # Check correct order
    assert round_structure.index("main") < round_structure.index("cleanup")

def test_get_phase_timing():
    """Test retrieving phase timing information."""
    # Test getting all phase timings
    all_timings = GameRulesService.get_phase_timing()
    
    assert "main" in all_timings
    assert "cleanup" in all_timings
    assert all_timings["main"] == 15
    assert all_timings["cleanup"] == 2
    
    # Test getting specific phase timing
    main_timing = GameRulesService.get_phase_timing("main")
    assert "main" in main_timing
    assert main_timing["main"] == 15

def test_advance_phase():
    """Test advancing the game phase."""
    # Test regular phase advancement
    result = GameRulesService.advance_phase("main")
    
    assert result["current_phase"] == "main"
    assert result["next_phase"] == "cleanup"
    assert result["new_round_starting"] is False
    assert result["phase_duration"] == 2  # Duration of cleanup phase
    
    # Test transition to new round
    result = GameRulesService.advance_phase("cleanup")
    
    assert result["current_phase"] == "cleanup"
    assert result["next_phase"] == "main"
    assert result["new_round_starting"] is True
    assert result["phase_duration"] == 15  # Duration of main phase
    
    # Test invalid phase
    result = GameRulesService.advance_phase("nonexistent")
    
    assert result["current_phase"] == "nonexistent"
    assert result["next_phase"] == "main"  # Default to first phase
    assert result["new_round_starting"] is False  # Can't determine if invalid phase

def test_check_communication_allowed():
    """Test checking if two civilizations can communicate."""
    # Test civilizations that can communicate
    result = GameRulesService.check_communication_allowed("Thrizoth", "Methane Collective")
    
    assert result["can_communicate"] is True
    assert "Thrizoth" in result["civilizations"]
    assert "Methane Collective" in result["civilizations"]
    
    # Test civilizations that cannot communicate
    result = GameRulesService.check_communication_allowed("Thrizoth", "Vasku")
    
    assert result["can_communicate"] is False
    assert "restriction_source" in result
    assert result["restriction_source"] in ["Thrizoth", "Vasku", "both"]
    
    # Test mutual restriction
    result = GameRulesService.check_communication_allowed("Methane Collective", "Glacian Current")
    
    assert result["can_communicate"] is False
    assert result["restriction_source"] in ["Methane Collective", "Glacian Current", "both"]

def test_get_law_constraints():
    """Test retrieving law system constraints."""
    constraints = GameRulesService.get_law_constraints()
    
    assert "law_duration" in constraints
    assert "max_active_laws" in constraints
    assert constraints["law_duration"] == 3
    assert constraints["max_active_laws"] == 6

def test_calculate_trade_costs():
    """Test calculating trade costs based on distance."""
    # Test standard distance
    result = GameRulesService.calculate_trade_costs(3)
    
    assert result["distance_jumps"] == 3
    assert result["base_cost"] == 15.0  # 3 * 5.0
    assert result["final_cost_percentage"] == 15.0  # Between min and max
    
    # Test short distance (below minimum)
    result = GameRulesService.calculate_trade_costs(1)
    
    assert result["distance_jumps"] == 1
    assert result["base_cost"] == 5.0  # 1 * 5.0
    assert result["final_cost_percentage"] == 10.0  # Bumped up to minimum
    
    # Test long distance (above maximum)
    result = GameRulesService.calculate_trade_costs(8)
    
    assert result["distance_jumps"] == 8
    assert result["base_cost"] == 40.0  # 8 * 5.0
    assert result["final_cost_percentage"] == 30.0  # Capped at maximum

def test_calculate_counterfeit_success():
    """Test calculating counterfeit operation success rates."""
    # Test basic case
    result = GameRulesService.calculate_counterfeit_success(5)
    
    assert result["base_success_rate"] == 50.0
    assert result["catalyst_quantity"] == 5
    assert result["additional_success_rate"] == 5
    assert result["final_success_rate"] == 55.0
    
    # Test maximum improvement
    result = GameRulesService.calculate_counterfeit_success(50)
    
    assert result["base_success_rate"] == 50.0
    assert result["catalyst_quantity"] == 50
    assert result["additional_success_rate"] == 25  # Capped at 25 (75 - 50)
    assert result["final_success_rate"] == 75.0  # Max rate

def test_calculate_intelligence_operation():
    """Test intelligence operation calculations."""
    # Test valid operation with sufficient resources
    result = GameRulesService.calculate_intelligence_operation(
        "Basic Resource Monitoring",
        {"Quantum Particles": 30, "Carbon Matrices": 35}
    )
    
    assert result["success"] is True
    assert result["operation_name"] == "Basic Resource Monitoring"
    assert result["base_success_rate"] == 60.0
    assert result["final_success_rate"] > 60.0  # Should be increased
    
    # Test valid operation with insufficient resources
    result = GameRulesService.calculate_intelligence_operation(
        "Basic Resource Monitoring",
        {"Quantum Particles": 10, "Carbon Matrices": 35}  # Not enough Quantum Particles
    )
    
    assert result["success"] is False
    assert "missing_resources" in result
    assert any(r["resource"] == "Quantum Particles" for r in result["missing_resources"])
    
    # Test invalid operation
    result = GameRulesService.calculate_intelligence_operation(
        "Nonexistent Operation",
        {"Quantum Particles": 30, "Carbon Matrices": 35}
    )
    
    assert result["success"] is False
    assert result["error"] == "Operation not found"