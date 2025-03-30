# tests/services/test_law_system_service.py
import unittest
from unittest.mock import patch, MagicMock
from uuid import uuid4

from app.services.law_system_service import LawSystemService
from app.config.law_system import LawSystemConfig, LawTemplate

class TestLawSystemService(unittest.TestCase):
    def setUp(self):
        # Create a real config for testing
        self.config = LawSystemConfig(config_id=uuid4())
        
        # Replace its templates with our test template
        self.template = LawTemplate(
            template_id="test_law",
            name="Test Law",
            description="A test law template",
            template_text="This law taxes [RESOURCE_TYPE] at [TAX_PERCENTAGE]%.",
            parameters=[
                {
                    "name": "RESOURCE_TYPE",
                    "type": "resource_type",
                    "description": "Resource to tax"
                },
                {
                    "name": "TAX_PERCENTAGE",
                    "type": "range",
                    "min": 5,
                    "max": 30,
                    "description": "Tax percentage"
                }
            ],
            effects={
                "type": "resource_tax",
                "applies_to": "trade"
            },
            category="economic"
        )
        
        # Clear existing templates and add only our test template
        self.config.law_templates = {"test_law": self.template}
        
        # Set up the patch for get_law_system_config
        self.patcher = patch('app.services.law_system_service.get_law_system_config')
        self.mock_get_config = self.patcher.start()
        self.mock_get_config.return_value = self.config
    
    def tearDown(self):
        # Stop the patcher
        self.patcher.stop()
    
    def test_get_available_templates(self):
        """Test retrieving available templates."""
        templates = LawSystemService.get_available_templates()
        self.assertEqual(len(templates), 1)
        self.assertEqual(templates[0]["template_id"], "test_law")
        self.assertEqual(templates[0]["name"], "Test Law")
        
        # Test filtering by category
        templates = LawSystemService.get_available_templates(category="economic")
        self.assertEqual(len(templates), 1)
        
        templates = LawSystemService.get_available_templates(category="non_existent")
        self.assertEqual(len(templates), 0)
    
    def test_get_template_details(self):
        """Test retrieving template details."""
        details = LawSystemService.get_template_details("test_law")
        self.assertEqual(details["template_id"], "test_law")
        self.assertEqual(details["name"], "Test Law")
        self.assertIn("parameters", details)
        self.assertIn("example", details)
        
        # Test with non-existent template
        details = LawSystemService.get_template_details("non_existent")
        self.assertIn("error", details)
    
    def test_validate_parameters(self):
        """Test parameter validation."""
        # Valid parameters
        valid_params = {
            "RESOURCE_TYPE": "Neutronium",
            "TAX_PERCENTAGE": "15"
        }
        
        is_valid, errors = LawSystemService.validate_parameters("test_law", valid_params)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
        
        # Invalid parameters - missing parameter
        invalid_params = {
            "RESOURCE_TYPE": "Neutronium"
            # Missing TAX_PERCENTAGE
        }
        
        is_valid, errors = LawSystemService.validate_parameters("test_law", invalid_params)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
        
        # Invalid parameters - out of range
        invalid_params = {
            "RESOURCE_TYPE": "Neutronium",
            "TAX_PERCENTAGE": "50"  # Above max of 30
        }
        
        is_valid, errors = LawSystemService.validate_parameters("test_law", invalid_params)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
        
        # Test with non-existent template
        is_valid, errors = LawSystemService.validate_parameters("non_existent", valid_params)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
    
    def test_create_law_proposal(self):
        """Test creating a law proposal."""
        # Valid proposal
        valid_params = {
            "RESOURCE_TYPE": "Neutronium",
            "TAX_PERCENTAGE": "15"
        }
        
        result = LawSystemService.create_law_proposal("test_law", valid_params, "Thrizoth")
        self.assertTrue(result["success"])
        self.assertIn("proposal", result)
        self.assertEqual(result["proposal"]["template_id"], "test_law")
        self.assertEqual(result["proposal"]["law_text"], "This law taxes Neutronium at 15%.")
        self.assertEqual(result["proposal"]["proposing_civilization"], "Thrizoth")
        self.assertEqual(result["proposal"]["votes"], ["Thrizoth"])  # Proposer voted for their law
        
        # Invalid proposal - invalid parameters
        invalid_params = {
            "RESOURCE_TYPE": "Neutronium",
            "TAX_PERCENTAGE": "50"  # Above max of 30
        }
        
        result = LawSystemService.create_law_proposal("test_law", invalid_params, "Thrizoth")
        self.assertFalse(result["success"])
        self.assertIn("errors", result)
        
        # Test with non-existent template
        result = LawSystemService.create_law_proposal("non_existent", valid_params, "Thrizoth")
        self.assertFalse(result["success"])
        self.assertIn("errors", result)
    
    def test_vote_on_law(self):
        """Test voting on a law proposal."""
        # Initialize current votes
        current_votes = {
            "proposal1": ["Thrizoth"]
        }
        
        # Valid vote
        result = LawSystemService.vote_on_law("proposal1", "Vasku", True, current_votes)
        self.assertTrue(result["success"])
        self.assertIn("proposal1", result["updated_votes"])
        self.assertIn("Vasku", result["updated_votes"]["proposal1"])
        
        # New proposal vote
        result = LawSystemService.vote_on_law("proposal2", "Glacian Current", True, current_votes)
        self.assertTrue(result["success"])
        self.assertIn("proposal2", result["updated_votes"])
        self.assertIn("Glacian Current", result["updated_votes"]["proposal2"])
        
        # Abstain vote - should fail since abstaining is not allowed by default
        self.config.voting_rules = {"abstain_allowed": False}
        result = LawSystemService.vote_on_law("proposal1", "Silicon Liberation", False, current_votes)
        self.assertFalse(result["success"])
        
        # Allow abstaining and test again
        self.config.voting_rules = {"abstain_allowed": True}
        result = LawSystemService.vote_on_law("proposal1", "Silicon Liberation", False, current_votes)
        self.assertTrue(result["success"])
        self.assertNotIn("Silicon Liberation", result["updated_votes"]["proposal1"])
    
    def test_resolve_law_votes(self):
        """Test resolving law votes."""
        # Create test proposals
        proposals = [
            {"id": "proposal1", "name": "Proposal 1"},
            {"id": "proposal2", "name": "Proposal 2"},
            {"id": "proposal3", "name": "Proposal 3"}
        ]
        
        # Clear winner
        current_votes = {
            "proposal1": ["Thrizoth", "Vasku"],
            "proposal2": ["Glacian Current"],
            "proposal3": []
        }
        
        result = LawSystemService.resolve_law_votes(proposals, current_votes)
        self.assertTrue(result["success"])
        self.assertEqual(result["winning_proposal"]["id"], "proposal1")
        self.assertEqual(result["vote_counts"]["proposal1"], 2)
        self.assertFalse(result["tie_occurred"])
        
        # Tie with no tiebreaker
        current_votes = {
            "proposal1": ["Thrizoth"],
            "proposal2": ["Glacian Current"]
        }
        
        self.config.voting_rules = {"tiebreaker": "none"}
        result = LawSystemService.resolve_law_votes(proposals, current_votes)
        self.assertFalse(result["success"])
        self.assertIn("tied_proposals", result)
        
        # Tie with "oldest_first" tiebreaker
        self.config.voting_rules = {"tiebreaker": "oldest_first"}
        result = LawSystemService.resolve_law_votes(proposals, current_votes)
        self.assertTrue(result["success"])
        self.assertEqual(result["winning_proposal"]["id"], "proposal1")  # First proposal wins
        self.assertTrue(result["tie_occurred"])
        
        # Test with no proposals
        result = LawSystemService.resolve_law_votes([], {})
        self.assertFalse(result["success"])
        self.assertIn("error", result)
    
    def test_check_law_conflicts(self):
        """Test checking for law conflicts."""
        # Create test laws
        new_law = {
            "category": "economic",
            "effects": {
                "type": "resource_tax"
            },
            "parameters": {
                "RESOURCE_TYPE": "Neutronium"
            }
        }
        
        existing_laws = [
            {
                "category": "economic",
                "effects": {
                    "type": "resource_tax"
                },
                "parameters": {
                    "RESOURCE_TYPE": "Neutronium"
                }
            },
            {
                "category": "economic",
                "effects": {
                    "type": "resource_tax"
                },
                "parameters": {
                    "RESOURCE_TYPE": "Crystal"
                }
            },
            {
                "category": "technology",
                "effects": {
                    "type": "project_restriction"
                }
            }
        ]
        
        conflicts = LawSystemService.check_law_conflicts(new_law, existing_laws)
        self.assertEqual(len(conflicts), 1)  # Should find one conflict (same resource)
        
        # Change resource type to test no conflict
        new_law["parameters"]["RESOURCE_TYPE"] = "Energy"
        conflicts = LawSystemService.check_law_conflicts(new_law, existing_laws)
        self.assertEqual(len(conflicts), 0)  # Should find no conflicts
    
    def test_calculate_law_effects(self):
        """Test calculating combined law effects."""
        # Create test laws
        active_laws = [
            {
                "effects": {
                    "type": "resource_tax",
                    "applies_to": "trade"
                },
                "parameters": {
                    "RESOURCE_TYPE": "Neutronium",
                    "TAX_PERCENTAGE": "15"
                }
            },
            {
                "effects": {
                    "type": "route_tax",
                    "applies_to": "trade"
                },
                "parameters": {
                    "REGION": "Alpha",
                    "TAX_PERCENTAGE": "10"
                }
            }
        ]
        
        # Test trading context
        trade_context = {
            "action_type": "trade",
            "resource_type": "Neutronium",
            "route": ["Alpha", "Beta"]
        }
        
        effects = LawSystemService.calculate_law_effects(active_laws, trade_context)
        self.assertEqual(effects["tax_percentage"], 25)  # 15% + 10%
        
        # Test context that doesn't match laws
        different_context = {
            "action_type": "trade",
            "resource_type": "Crystal",  # Different resource
            "route": ["Beta", "Gamma"]  # Different route
        }
        
        effects = LawSystemService.calculate_law_effects(active_laws, different_context)
        self.assertEqual(effects["tax_percentage"], 0)  # No matching laws
        
        # Test project development context
        project_law = {
            "effects": {
                "type": "project_restriction",
                "applies_to": "specific_project"
            },
            "parameters": {
                "PROJECT_NAME": "Dyson Sphere",
                "LICENSE_COST": "200",
                "RESOURCE_TYPE": "Crystal"
            }
        }
        
        active_laws.append(project_law)
        
        project_context = {
            "action_type": "project_development",
            "project_name": "Dyson Sphere"
        }
        
        effects = LawSystemService.calculate_law_effects(active_laws, project_context)
        self.assertEqual(effects["license_cost"], 200)
        self.assertEqual(effects["resource_requirements"]["Crystal"], 200)

if __name__ == '__main__':
    unittest.main()