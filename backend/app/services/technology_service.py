# app/services/technology_service.py
from typing import Dict, List, Optional, Any
from uuid import UUID

from app.config.utils import get_technology_config

class TechnologyService:
    """
    Service for technology-related operations using the configuration system.
    
    This service provides methods that leverage technology configuration to 
    implement game logic related to technology development, requirements checking,
    and project management.
    """
    
    @staticmethod
    def get_available_technologies(civilization_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all technologies available to a specific civilization, categorized by type.
        
        Args:
            civilization_id: The ID or name of the civilization
            
        Returns:
            Dictionary with tech types as keys and lists of technologies as values
        """
        tech_config = get_technology_config()
        return tech_config.get_technologies_for_civilization(civilization_id)
    
    @staticmethod
    def get_technology_details(tech_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific technology.
        
        Args:
            tech_id: The ID of the technology
            
        Returns:
            Dictionary with technology details including requirements
        """
        tech_config = get_technology_config()
        
        # Get the component
        component = tech_config.components.get(tech_id)
        if not component:
            return {"error": "Technology not found"}
        
        # Get requirements
        requirements = tech_config.get_development_requirements(tech_id)
        req_details = []
        for req in requirements:
            req_details.append({
                "id": req.required_id,
                "type": req.required_type,
                "quantity": req.quantity
            })
        
        # For universal projects, get effects
        effects = {}
        if component.tech_type == "universal_project":
            effects = tech_config.project_effects.get(tech_id, {})
        
        return {
            "id": tech_id,
            "name": component.name,
            "description": component.description,
            "type": component.tech_type,
            "group": component.tech_group,
            "requirements": req_details,
            "effects": effects
        }
    
    @staticmethod
    def check_development_prerequisites(civilization_id: str, tech_id: str, 
                                      available_resources: Optional[Dict[str, int]] = None) -> Dict[str, Any]:
        """
        Check if a civilization can develop a specific technology.
        
        Args:
            civilization_id: The ID or name of the civilization
            tech_id: The ID of the technology
            available_resources: Optional dictionary of resources the civilization has
            
        Returns:
            Dictionary with prerequisite check results
        """
        tech_config = get_technology_config()
        
        # First check if civilization is technically capable
        if not tech_config.can_civilization_develop(civilization_id, tech_id):
            return {
                "can_develop": False,
                "reason": "This technology is not available to your civilization",
                "details": {
                    "tech_id": tech_id,
                    "civilization_id": civilization_id
                }
            }
        
        # Get the technology component
        component = tech_config.components.get(tech_id)
        if not component:
            return {
                "can_develop": False,
                "reason": "Technology not found",
                "details": {"tech_id": tech_id}
            }
        
        # Get requirements
        requirements = tech_config.get_development_requirements(tech_id)
        missing_requirements = []
        
        if available_resources:
            # Check resource requirements
            for req in requirements:
                if req.required_type == "resource":
                    available = available_resources.get(req.required_id, 0)
                    if available < req.quantity:
                        missing_requirements.append({
                            "id": req.required_id,
                            "type": req.required_type,
                            "required": req.quantity,
                            "available": available
                        })
                else:
                    # For tech requirements, we'd need to check inventory in real implementation
                    # Here we'll just assume they're missing
                    missing_requirements.append({
                        "id": req.required_id,
                        "type": req.required_type,
                        "required": req.quantity,
                        "available": 0
                    })
        else:
            # Without resource info, we can only check capability, not resources
            return {
                "can_develop": True,
                "reason": "Technology is available, but resource check cannot be performed",
                "details": {
                    "tech_id": tech_id,
                    "requirements": [
                        {
                            "id": req.required_id,
                            "type": req.required_type,
                            "quantity": req.quantity
                        } for req in requirements
                    ]
                }
            }
        
        if missing_requirements:
            return {
                "can_develop": False,
                "reason": "Missing required resources or components",
                "missing_requirements": missing_requirements
            }
        
        return {
            "can_develop": True,
            "details": {
                "tech_id": tech_id,
                "name": component.name,
                "type": component.tech_type
            }
        }
    
    @staticmethod
    def get_technology_tree(tech_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Get the technology dependency tree for visualization or analysis.
        
        Args:
            tech_type: Optional filter for technology type
            
        Returns:
            Technology tree structure
        """
        tech_config = get_technology_config()
        return tech_config.get_technology_tree(tech_type)
    
    @staticmethod
    def get_project_effect(project_id: str, civilization_id: str) -> Dict[str, Any]:
        """
        Get the effect of a universal project on a specific civilization.
        
        Args:
            project_id: The ID of the universal project
            civilization_id: The ID of the civilization
            
        Returns:
            Dictionary with effect details
        """
        tech_config = get_technology_config()
        return tech_config.get_project_effect(project_id, civilization_id)