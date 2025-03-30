# tests/config/test_intel_operations.py
import unittest
from uuid import uuid4

from app.config.intel_operations import IntelOperationsConfig, IntelOperation

class TestIntelOperationsConfig(unittest.TestCase):
    def setUp(self):
        self.config = IntelOperationsConfig(config_id=uuid4())
    
    def test_initialization(self):
        """Test that the config initializes with default values."""
        self.assertIsNotNone(self.config.operations)
        self.assertGreater(len(self.config.operations), 0)
        self.assertIsNotNone(self.config.success_rate_rules)
        self.assertIsNotNone(self.config.defense_rules)
    
    def test_get_operation(self):
        """Test retrieving an operation by ID."""
        # Using an operation ID that should exist in defaults
        operation = self.config.get_operation("basic_resource_monitoring")
        self.assertIsNotNone(operation)
        self.assertEqual(operation.name, "Basic Resource Monitoring")
        
        # Test with non-existent operation
        operation = self.config.get_operation("non_existent_operation")
        self.assertIsNone(operation)
    
    def test_get_operations_for_civilization(self):
        """Test retrieving operations available to a civilization."""
        # Test universal operations (available to all)
        operations = self.config.get_operations_for_civilization("Thrizoth")
        self.assertGreater(len(operations), 0)
        
        # Test with small tech requirements
        operations_with_tech = self.config.get_operations_for_civilization(
            "Thrizoth", ["rapid_growth_fertilizer"]
        )
        self.assertGreater(len(operations_with_tech), len(operations))
        
        # Verify civilization-specific operations aren't available to others
        thrizoth_ops = set(op.operation_id for op in self.config.get_operations_for_civilization(
            "Thrizoth", ["rapid_growth_fertilizer"]
        ))
        methane_ops = set(op.operation_id for op in self.config.get_operations_for_civilization(
            "Methane Collective", ["pressure_regulators"]
        ))
        # There should be some difference in available operations
        self.assertTrue(thrizoth_ops.symmetric_difference(methane_ops))
    
    def test_calculate_success_rate(self):
        """Test calculating success rate with resource investment."""
        # Test with no additional resources
        success_rate = self.config.calculate_success_rate(
            "basic_resource_monitoring", {}
        )
        operation = self.config.get_operation("basic_resource_monitoring")
        self.assertEqual(success_rate, operation.base_success_rate)
        
        # Test with additional resources
        success_rate = self.config.calculate_success_rate(
            "basic_resource_monitoring", 
            {"Quantum Particles": 25, "Carbon Matrices": 25}
        )
        self.assertGreater(success_rate, operation.base_success_rate)
        
        # Test with excessive resources (should cap at maximum)
        max_improvement = self.config.success_rate_rules.get("max_additional_success_rate")
        success_rate = self.config.calculate_success_rate(
            "basic_resource_monitoring", 
            {"Quantum Particles": 500, "Carbon Matrices": 500}
        )
        self.assertLessEqual(
            success_rate, 
            operation.base_success_rate + max_improvement
        )
        
        # Test with invalid operation
        success_rate = self.config.calculate_success_rate(
            "non_existent_operation", 
            {"Quantum Particles": 25}
        )
        self.assertEqual(success_rate, 0.0)
    
    def test_validation(self):
        """Test validation of the configuration."""
        # The default configuration should be valid
        self.assertTrue(self.config.validate())
        
        # Create an invalid configuration
        invalid_config = IntelOperationsConfig(config_id=uuid4())
        invalid_config.operations = {}  # Empty operations should be invalid
        self.assertFalse(invalid_config.validate())
        
        # Create an invalid operation with out-of-range success rate
        invalid_operation = IntelOperation(
            operation_id="invalid_operation",
            name="Invalid Operation",
            description="An operation with invalid success rate",
            base_cost={"Resource": 10},
            base_success_rate=120.0,  # Invalid: > 100%
            additional_cost_per_point={"Resource": 5}
        )
        
        invalid_config = IntelOperationsConfig(config_id=uuid4())
        invalid_config.operations = {"invalid_operation": invalid_operation}
        self.assertFalse(invalid_config.validate())
    
    def test_to_dict_and_from_dict(self):
        """Test serialization and deserialization."""
        # Convert to dictionary
        config_dict = self.config.to_dict()
        self.assertIsNotNone(config_dict)
        self.assertIn("operations", config_dict)
        self.assertIn("success_rate_rules", config_dict)
        self.assertIn("defense_rules", config_dict)
        
        # Create new config from dictionary
        new_config = IntelOperationsConfig.from_dict(config_dict)
        self.assertEqual(len(new_config.operations), len(self.config.operations))
        self.assertEqual(new_config.success_rate_rules, self.config.success_rate_rules)
        self.assertEqual(new_config.defense_rules, self.config.defense_rules)
        
        # Check a specific operation
        original_op = self.config.get_operation("basic_resource_monitoring")
        new_op = new_config.get_operation("basic_resource_monitoring")
        self.assertEqual(new_op.name, original_op.name)
        self.assertEqual(new_op.base_success_rate, original_op.base_success_rate)

if __name__ == '__main__':
    unittest.main()