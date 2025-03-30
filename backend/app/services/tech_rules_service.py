# app/services/tech_rules_service.py
"""
Technology Service Module

This module provides functionality for technology-related operations in the Stellar Accord game.
It leverages the technology configuration system to manage technology development, 
requirements checking, and project management without hard-coding technology knowledge.
"""

from typing import Dict, List, Optional, Any
from app.config.utils import get_technology_config, get_star_map_config
from app.services.map_service import MapService

class TechnologyService:
    """
    Service for technology-related operations using the configuration system.
    
    This service provides methods for checking technology requirements,
    validating development possibilities, and calculating project requirements
    based on the technology configuration.
    """
    
    @staticmethod
    def get_available_technologies(civilization_id: str) -> List[Dict[str, Any]]:
        """
        Get all technologies available to a specific civilization.
        
        This method uses the technology configuration to determine
        which technology components a civilization is capable of developing
        based on their capabilities.
        
        Args:
            civilization_id: The ID of the civilization
            
        Returns:
            A list of technology component information dictionaries
        """
        tech_config = get_technology_config()
        
        available_techs = []
        for component_id, component in tech_config.components.items():
            if tech_config.can_civilization_develop(civilization_id, component_id):
                available_techs.append({
                    "component_id": component_id,
                    "name": component.name,
                    "description": component.description,
                    "tech_type": component.tech_type,
                    "tech_group": component.tech_group
                })
        
        return available_techs
    
    @staticmethod
    def get_component_requirements(component_id: str) -> List[Dict[str, Any]]:
        """
        Get all requirements for developing a technology component.
        
        Args:
            component_id: The ID of the technology component
            
        Returns:
            A list of requirement dictionaries
        """
        tech_config = get_technology_config()
        
        requirements = []
        for req in tech_config.get_development_requirements(component_id):
            requirements.append({
                "required_id": req.required_id,
                "required_type": req.required_type,
                "quantity": req.quantity
            })
        
        return requirements
    
    @staticmethod
    def check_development_prerequisites(civilization_id: str, component_id: str) -> Dict[str, Any]:
        """
        Check if a civilization has the prerequisites to develop a technology.
        
        This method checks:
        1. If the civilization is technically capable of the technology
        2. The required resources and components
        
        Args:
            civilization_id: The ID of the civilization
            component_id: The ID of the technology component
            
        Returns:
            Dictionary with prerequisites status
        """
        tech_config = get_technology_config()
        
        # Check if civilization can develop this technology
        if not tech_config.can_civilization_develop(civilization_id, component_id):
            return {
                "can_develop": False,
                "reason": "Technology pathway not available to this civilization",
                "missing_prerequisites": []
            }
        
        # Get requirements
        requirements = tech_config.get_development_requirements(component_id)
        
        # Get component if it exists
        component = tech_config.components.get(component_id)
        if not component:
            return {
                "can_develop": False,
                "reason": "Technology component does not exist",
                "missing_prerequisites": []
            }
            
        # In a real implementation, you would check against the game state
        # to see if the civilization has the required resources and prerequisite technologies
        # For this example, we'll just return the requirements
        
        return {
            "can_develop": True,  # Simplified for this example
            "component": {
                "component_id": component_id,
                "name": component.name,
                "description": component.description,
                "tech_type": component.tech_type,
                "tech_group": component.tech_group
            },
            "requirements": [
                {
                    "required_id": req.required_id,
                    "required_type": req.required_type,
                    "quantity": req.quantity,
                    "is_fulfilled": False  # Would be determined by game state
                }
                for req in requirements
            ]
        }