# tests/config/test_technology_validation.py
import pytest
from app.config.technology import TechnologyConfig

def test_technology_config_validation():
    """Test that the default TechnologyConfig passes validation."""
    config = TechnologyConfig()
    assert config.validate(), "Default TechnologyConfig should pass validation"
    
    # Print debug information if validation failed
    if not config.validate():
        # Print all components
        print("\nComponents:")
        for comp_id in config.components:
            print(f"  - {comp_id}")
            
        # Print all requirements
        print("\nRequirements:")
        for comp_id, reqs in config.requirements.items():
            print(f"  - {comp_id}: {len(reqs)} requirements")
            for req in reqs:
                print(f"    - {req.required_type}: {req.required_id}")
        
        # Print project effects
        print("\nProject effects:")
        for proj_id in config.project_effects:
            print(f"  - {proj_id}")