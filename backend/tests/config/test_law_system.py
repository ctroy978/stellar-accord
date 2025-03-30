# tests/config/test_law_system.py
import unittest
from uuid import uuid4

from app.config.law_system import LawSystemConfig, LawTemplate

class TestLawSystemConfig(unittest.TestCase):
    def setUp(self):
        self.config = LawSystemConfig(config_id=uuid4())
    
    def test_initialization(self):
        """Test that the config initializes with default values."""
        self.assertIsNotNone(self.config.law_templates)
        self.assertGreater(len(self.config.law_templates), 0)
        self.assertIsNotNone(self.config.max_laws_per_category)
        self.assertIsNotNone(self.config.voting_rules)
    
    def test_get_template(self):
        """Test retrieving a template by ID."""
        # Using a template ID that should exist in defaults
        template = self.config.get_template("resource_tax_law")
        self.assertIsNotNone(template)
        self.assertEqual(template.name, "Resource Tax Law")
        
        # Test with non-existent template
        template = self.config.get_template("non_existent_template")
        self.assertIsNone(template)
    
    def test_get_templates_by_category(self):
        """Test retrieving templates by category."""
        # Get templates from the "economic" category
        templates = self.config.get_templates_by_category("economic")
        self.assertGreater(len(templates), 0)
        for template in templates:
            self.assertEqual(template.category, "economic")
        
        # Test with non-existent category
        templates = self.config.get_templates_by_category("non_existent_category")
        self.assertEqual(len(templates), 0)
        
        # Test with no category (should return all templates)
        all_templates = self.config.get_templates_by_category()
        self.assertEqual(len(all_templates), len(self.config.law_templates))
    
    def test_get_max_laws(self):
        """Test retrieving max laws for a category."""
        # Test with a category that should exist
        max_laws = self.config.get_max_laws("economic")
        self.assertGreater(max_laws, 0)
        
        # Test with non-existent category
        max_laws = self.config.get_max_laws("non_existent_category")
        self.assertEqual(max_laws, 0)
    
    def test_render_law_text(self):
        """Test rendering law text with parameters."""
        # Test with existing template
        parameters = {
            "RESOURCE_TYPE": "Neutronium",
            "TAX_PERCENTAGE": "15"
        }
        
        expected_text = "Trading of Neutronium requires a tax payment of 15% to the Kokoro Conclave treasury."
        rendered_text = self.config.render_law_text("resource_tax_law", parameters)
        self.assertEqual(rendered_text, expected_text)
        
        # Test with non-existent template
        rendered_text = self.config.render_law_text("non_existent_template", parameters)
        self.assertEqual(rendered_text, "")
    
    def test_calculate_effects(self):
        """Test calculating law effects."""
        # Test with existing template
        parameters = {
            "RESOURCE_TYPE": "Neutronium",
            "TAX_PERCENTAGE": "15"
        }
        
        effects = self.config.calculate_effects("resource_tax_law", parameters)
        self.assertIsNotNone(effects)
        self.assertEqual(effects["type"], "resource_tax")
        self.assertEqual(effects["applies_to"], "trade")
        self.assertEqual(effects["parameters"]["RESOURCE_TYPE"], "Neutronium")
        self.assertEqual(effects["parameters"]["TAX_PERCENTAGE"], "15")
        
        # Test with non-existent template
        effects = self.config.calculate_effects("non_existent_template", parameters)
        self.assertEqual(effects, {})
    
    def test_validation(self):
        """Test validation of the configuration."""
        # The default configuration should be valid
        self.assertTrue(self.config.validate())
        
        # Create an invalid configuration
        invalid_config = LawSystemConfig(config_id=uuid4())
        invalid_config.law_templates = {}  # Empty templates should be invalid
        self.assertFalse(invalid_config.validate())
        
        # Create an invalid template with missing parameter
        invalid_template = LawTemplate(
            template_id="invalid_template",
            name="Invalid Template",
            description="A template with missing parameter",
            template_text="This template has a [MISSING_PARAM] that is not defined.",
            parameters=[]  # No parameters defined
        )
        
        invalid_config = LawSystemConfig(config_id=uuid4())
        invalid_config.law_templates = {"invalid_template": invalid_template}
        self.assertFalse(invalid_config.validate())
    
    def test_to_dict_and_from_dict(self):
        """Test serialization and deserialization."""
        # Convert to dictionary
        config_dict = self.config.to_dict()
        self.assertIsNotNone(config_dict)
        self.assertIn("law_templates", config_dict)
        self.assertIn("max_laws_per_category", config_dict)
        self.assertIn("voting_rules", config_dict)
        
        # Create new config from dictionary
        new_config = LawSystemConfig.from_dict(config_dict)
        self.assertEqual(len(new_config.law_templates), len(self.config.law_templates))
        self.assertEqual(new_config.max_laws_per_category, self.config.max_laws_per_category)
        self.assertEqual(new_config.voting_rules, self.config.voting_rules)
        
        # Check a specific template
        original_template = self.config.get_template("resource_tax_law")
        new_template = new_config.get_template("resource_tax_law")
        self.assertEqual(new_template.name, original_template.name)
        self.assertEqual(new_template.template_text, original_template.template_text)

if __name__ == '__main__':
    unittest.main()