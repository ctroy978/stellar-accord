# tests/services/test_intel_operations_service.py
import pytest
from app.services.intel_operations_service import IntelOperationsService

def test_get_available_operations():
    """Test retrieving available operations for a civilization."""
    # Get operations for Thrizoth with no small tech
    operations = IntelOperationsService.get_available_operations("Thrizoth")
    
    # Verify we have universal operations
    assert len(operations) > 0
    
    # Verify format of operations
    first_op = operations[0]
    assert "id" in first_op
    assert "name" in first_op
    assert "description" in first_op
    assert "base_cost" in first_op
    assert "base_success_rate" in first_op
    
    # Get operations with small tech
    operations_with_tech = IntelOperationsService.get_available_operations(
        "Thrizoth", ["rapid_growth_fertilizer"]
    )
    
    # Should have more operations with small tech
    assert len(operations_with_tech) > len(operations)
    
    # Verify civilization specific operations differ
    thrizoth_ops = [op["id"] for op in IntelOperationsService.get_available_operations(
        "Thrizoth", ["rapid_growth_fertilizer"]
    )]
    
    silicon_ops = [op["id"] for op in IntelOperationsService.get_available_operations(
        "Silicon Liberation", ["encryption_algorithm"]
    )]
    
    # There should be a difference in available operations
    assert set(thrizoth_ops) != set(silicon_ops)

def test_get_operation_details():
    """Test retrieving operation details."""
    # Get details for a universal operation
    details = IntelOperationsService.get_operation_details("basic_resource_monitoring")
    
    assert details["id"] == "basic_resource_monitoring"
    assert details["name"] == "Basic Resource Monitoring"
    assert "base_cost" in details
    assert "base_success_rate" in details
    assert "additional_cost_per_point" in details
    
    # Test nonexistent operation
    details = IntelOperationsService.get_operation_details("nonexistent_operation")
    assert "error" in details

def test_calculate_operation_success():
    """Test calculating operation success rates."""
    # Test with no additional resources
    result = IntelOperationsService.calculate_operation_success(
        "basic_resource_monitoring", {}
    )
    assert result["success"] is True
    assert result["calculated_success_rate"] == result["base_success_rate"]
    
    # Test with additional resources
    result = IntelOperationsService.calculate_operation_success(
        "basic_resource_monitoring", 
        {"Quantum Particles": 25, "Carbon Matrices": 25}
    )
    assert result["calculated_success_rate"] > result["base_success_rate"]
    
    # Test with defense
    result = IntelOperationsService.calculate_operation_success(
        "resource_theft", 
        {"Duranium Alloy": 30, "Temporal Dust": 20}, 
        defense_level=30.0
    )
    assert result["effective_success_rate"] < result["calculated_success_rate"]
    
    # Test nonexistent operation
    result = IntelOperationsService.calculate_operation_success(
        "nonexistent_operation", {}
    )
    assert result["success"] is False

def test_validate_operation_resources():
    """Test validating resource requirements for operations."""
    # Test with sufficient resources
    result = IntelOperationsService.validate_operation_resources(
        "basic_resource_monitoring", 
        {"Quantum Particles": 30, "Carbon Matrices": 30}
    )
    assert result["valid"] is True
    
    # Should include remaining resources after base cost
    assert result["additional_resources"]["Quantum Particles"] > 0
    assert result["additional_resources"]["Carbon Matrices"] > 0
    
    # Test with insufficient resources
    result = IntelOperationsService.validate_operation_resources(
        "basic_resource_monitoring", 
        {"Quantum Particles": 10, "Carbon Matrices": 30}
    )
    assert result["valid"] is False
    assert "missing_resources" in result
    
    # Test nonexistent operation
    result = IntelOperationsService.validate_operation_resources(
        "nonexistent_operation", 
        {"Quantum Particles": 30}
    )
    assert result["valid"] is False