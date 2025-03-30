# app/services/law_system_service.py
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID

from app.config.utils import get_law_system_config

class LawSystemService:
    """
    Service for law system operations using the configuration system.
    
    This service provides methods that leverage the law system configuration to
    implement game mechanics related to laws, voting, and enforcement.
    """
    
    @staticmethod
    def get_available_templates(category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all available law templates, optionally filtered by category.
        
        Args:
            category: Optional category to filter by
            
        Returns:
            List of template information dictionaries
        """
        law_config = get_law_system_config()
        
        templates = law_config.get_templates_by_category(category)
        
        return [
            {
                "template_id": template.template_id,
                "name": template.name,
                "description": template.description,
                "category": template.category,
                "parameters": template.parameters
            }
            for template in templates
        ]
    
    @staticmethod
    def get_template_details(template_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific law template.
        
        Args:
            template_id: The ID of the template
            
        Returns:
            Dictionary with template details
        """
        law_config = get_law_system_config()
        
        template = law_config.get_template(template_id)
        if not template:
            return {"error": "Template not found"}
        
        return {
            "template_id": template.template_id,
            "name": template.name,
            "description": template.description,
            "template_text": template.template_text,
            "parameters": template.parameters,
            "category": template.category,
            "example": law_config.render_law_text(template_id, 
                                                {p["name"]: "[Example value]" for p in template.parameters})
        }
    
    @staticmethod
    def validate_parameters(template_id: str, parameters: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate that the provided parameters are correct for the template.
        
        Args:
            template_id: The ID of the template
            parameters: Dictionary of parameter values
            
        Returns:
            Tuple of (is_valid, list_of_error_messages)
        """
        law_config = get_law_system_config()
        
        template = law_config.get_template(template_id)
        if not template:
            return False, ["Template not found"]
        
        errors = []
        
        # Check all required parameters are present
        for param_def in template.parameters:
            param_name = param_def["name"]
            if param_name not in parameters:
                errors.append(f"Missing required parameter: {param_name}")
                continue
            
            # Validate parameter type and value
            param_value = parameters[param_name]
            param_type = param_def["type"]
            
            if param_type == "range":
                min_val = param_def.get("min", 0)
                max_val = param_def.get("max", float("inf"))
                
                try:
                    numeric_value = float(param_value)
                    if numeric_value < min_val or numeric_value > max_val:
                        errors.append(f"Parameter {param_name} must be between {min_val} and {max_val}")
                except (ValueError, TypeError):
                    errors.append(f"Parameter {param_name} must be a number")
            
            elif param_type == "number":
                try:
                    float(param_value)
                except (ValueError, TypeError):
                    errors.append(f"Parameter {param_name} must be a number")
            
            # Other parameter types would be validated against game state in a real implementation
            # For now, we'll just check they are strings
            elif param_type in ["resource_category", "resource_type", "project", 
                               "uber_tech", "star_system", "text", "civilization_list"]:
                if not isinstance(param_value, str) and not isinstance(param_value, list):
                    errors.append(f"Parameter {param_name} has invalid type")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def create_law_proposal(template_id: str, parameters: Dict[str, Any], 
                          proposing_civilization: str) -> Dict[str, Any]:
        """
        Create a law proposal from a template and parameters.
        
        Args:
            template_id: The ID of the template
            parameters: Dictionary of parameter values
            proposing_civilization: The civilization proposing the law
            
        Returns:
            Dictionary with the law proposal
        """
        law_config = get_law_system_config()
        
        # Validate parameters
        is_valid, errors = LawSystemService.validate_parameters(template_id, parameters)
        if not is_valid:
            return {
                "success": False,
                "errors": errors
            }
        
        template = law_config.get_template(template_id)
        if not template:
            return {
                "success": False,
                "errors": ["Template not found"]
            }
        
        # Render the law text
        law_text = law_config.render_law_text(template_id, parameters)
        
        # Calculate the effects
        effects = law_config.calculate_effects(template_id, parameters)
        
        return {
            "success": True,
            "proposal": {
                "template_id": template_id,
                "template_name": template.name,
                "parameters": parameters,
                "category": template.category,
                "law_text": law_text,
                "effects": effects,
                "proposing_civilization": proposing_civilization,
                "votes": [proposing_civilization]  # Proposer automatically votes for their law
            }
        }
    
    @staticmethod
    def vote_on_law(proposal_id: str, voting_civilization: str, 
                  vote: bool, current_votes: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Record a civilization's vote on a law proposal.
        
        Args:
            proposal_id: ID of the law proposal
            voting_civilization: The civilization casting the vote
            vote: True for yes, False for no/abstain
            current_votes: Current vote tally for all proposals
            
        Returns:
            Updated vote information
        """
        law_config = get_law_system_config()
        
        # Check if abstaining is allowed
        if not vote and not law_config.voting_rules.get("abstain_allowed", False):
            return {
                "success": False,
                "error": "Abstaining from voting is not allowed"
            }
        
        # Update votes (in a real implementation, this would update the database)
        if vote:
            if proposal_id not in current_votes:
                current_votes[proposal_id] = []
            
            if voting_civilization not in current_votes[proposal_id]:
                current_votes[proposal_id].append(voting_civilization)
        
        return {
            "success": True,
            "updated_votes": current_votes
        }
    
    @staticmethod
    def resolve_law_votes(proposals: List[Dict[str, Any]], 
                        current_votes: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Determine which law proposal wins based on votes.
        
        Args:
            proposals: List of law proposals
            current_votes: Dictionary mapping proposal IDs to lists of voting civilizations
            
        Returns:
            Dictionary with the winning proposal and vote information
        """
        law_config = get_law_system_config()
        
        # Count votes for each proposal
        vote_counts = {}
        for proposal in proposals:
            proposal_id = proposal.get("id", str(proposal))
            votes = current_votes.get(proposal_id, [])
            vote_counts[proposal_id] = len(votes)
        
        # Find the proposal(s) with the most votes
        if not vote_counts:
            return {
                "success": False,
                "error": "No proposals to resolve"
            }
        
        max_votes = max(vote_counts.values())
        winners = [pid for pid, count in vote_counts.items() if count == max_votes]
        
        # Handle tie according to rules
        winning_id = None
        if len(winners) == 1:
            winning_id = winners[0]
        else:
            tiebreaker = law_config.voting_rules.get("tiebreaker", "none")
            
            if tiebreaker == "none":
                return {
                    "success": False,
                    "error": "Tied vote with no tiebreaker rule",
                    "tied_proposals": winners
                }
            elif tiebreaker == "random":
                import random
                winning_id = random.choice(winners)
            elif tiebreaker == "oldest_first":
                # In a real implementation, we'd check timestamps
                winning_id = winners[0]
        
        # Find the winning proposal
        winning_proposal = None
        for proposal in proposals:
            if proposal.get("id", str(proposal)) == winning_id:
                winning_proposal = proposal
                break
        
        return {
            "success": True,
            "winning_proposal": winning_proposal,
            "vote_counts": vote_counts,
            "tie_occurred": len(winners) > 1
        }
    
    @staticmethod
    def check_law_conflicts(new_law: Dict[str, Any], 
                          existing_laws: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Check if a new law conflicts with existing laws.
        
        Args:
            new_law: The new law being enacted
            existing_laws: List of currently active laws
            
        Returns:
            List of conflicting laws
        """
        # In a real implementation, we would have more sophisticated conflict detection
        # based on the law's effects and category
        
        conflicts = []
        
        new_category = new_law.get("category")
        new_effects = new_law.get("effects", {})
        new_effect_type = new_effects.get("type")
        
        for existing_law in existing_laws:
            existing_category = existing_law.get("category")
            existing_effects = existing_law.get("effects", {})
            existing_effect_type = existing_effects.get("type")
            
            # Check for conflicts in the same category with same effect type
            if (new_category == existing_category and 
                new_effect_type == existing_effect_type):
                
                # Check for specific conflicts
                if new_effect_type in ["resource_tax", "route_tax"] and existing_effect_type in ["resource_tax", "route_tax"]:
                    # Check if they're taxing the same thing
                    new_resource = new_law.get("parameters", {}).get("RESOURCE_TYPE")
                    existing_resource = existing_law.get("parameters", {}).get("RESOURCE_TYPE")
                    
                    if new_resource == existing_resource:
                        conflicts.append(existing_law)
                
                elif new_effect_type == "project_restriction":
                    # Check if restricting the same project
                    new_project = new_law.get("parameters", {}).get("PROJECT_NAME")
                    existing_project = existing_law.get("parameters", {}).get("PROJECT_NAME")
                    
                    if new_project == existing_project:
                        conflicts.append(existing_law)
        
        return conflicts
    
    @staticmethod
    def calculate_law_effects(active_laws: List[Dict[str, Any]], 
                            context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate the combined effects of all active laws on a specific action.
        
        Args:
            active_laws: List of active laws
            context: Dictionary with information about the action being performed
            
        Returns:
            Dictionary with calculated effects
        """
        effects = {
            "tax_percentage": 0,
            "license_cost": 0,
            "resource_requirements": {},
            "restrictions": []
        }
        
        action_type = context.get("action_type")
        
        for law in active_laws:
            law_effects = law.get("effects", {})
            law_type = law_effects.get("type")
            law_applies_to = law_effects.get("applies_to")
            
            # Skip laws that don't apply to this action
            if action_type == "trade" and law_applies_to != "trade":
                continue
            elif action_type == "project_development" and law_applies_to not in ["specific_project", "universal_projects"]:
                continue
            
            # Apply effects based on law type
            if law_type == "resource_tax" and action_type == "trade":
                # Check if the trade involves the taxed resource
                taxed_resource = law.get("parameters", {}).get("RESOURCE_TYPE")
                trade_resource = context.get("resource_type")
                
                if taxed_resource == trade_resource or taxed_resource == "ALL":
                    tax_rate = float(law.get("parameters", {}).get("TAX_PERCENTAGE", 0))
                    effects["tax_percentage"] += tax_rate
            
            elif law_type == "route_tax" and action_type == "trade":
                # Check if the trade route goes through the taxed region
                taxed_region = law.get("parameters", {}).get("REGION")
                trade_route = context.get("route", [])
                
                if taxed_region in trade_route:
                    tax_rate = float(law.get("parameters", {}).get("TAX_PERCENTAGE", 0))
            
            return effects
    

    @staticmethod
    def calculate_law_effects(active_laws: List[Dict[str, Any]], 
                            context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate the combined effects of all active laws on a specific action.
        
        Args:
            active_laws: List of active laws
            context: Dictionary with information about the action being performed
            
        Returns:
            Dictionary with calculated effects
        """
        effects = {
            "tax_percentage": 0,
            "license_cost": 0,
            "resource_requirements": {},
            "restrictions": []
        }
        
        action_type = context.get("action_type")
        
        for law in active_laws:
            law_effects = law.get("effects", {})
            law_type = law_effects.get("type")
            law_applies_to = law_effects.get("applies_to")
            
            # Skip laws that don't apply to this action
            if action_type == "trade" and law_applies_to != "trade":
                continue
            elif action_type == "project_development" and law_applies_to not in ["specific_project", "universal_projects"]:
                continue
            
            # Apply effects based on law type
            if law_type == "resource_tax" and action_type == "trade":
                # Check if the trade involves the taxed resource
                taxed_resource = law.get("parameters", {}).get("RESOURCE_TYPE")
                trade_resource = context.get("resource_type")
                
                if taxed_resource == trade_resource or taxed_resource == "ALL":
                    tax_rate = float(law.get("parameters", {}).get("TAX_PERCENTAGE", 0))
                    effects["tax_percentage"] += tax_rate
            
            elif law_type == "route_tax" and action_type == "trade":
                # Check if the trade route goes through the taxed region
                taxed_region = law.get("parameters", {}).get("REGION")
                trade_route = context.get("route", [])
                
                if taxed_region in trade_route:
                    tax_rate = float(law.get("parameters", {}).get("TAX_PERCENTAGE", 0))
                    effects["tax_percentage"] += tax_rate
            
            elif law_type == "project_restriction" and action_type == "project_development":
                # Check if this restricts the project being developed
                restricted_project = law.get("parameters", {}).get("PROJECT_NAME")
                project_name = context.get("project_name")
                
                if restricted_project == project_name:
                    # Add licensing cost
                    license_cost = int(law.get("parameters", {}).get("LICENSE_COST", 0))
                    resource_type = law.get("parameters", {}).get("RESOURCE_TYPE")
                    
                    effects["license_cost"] += license_cost
                    if resource_type not in effects["resource_requirements"]:
                        effects["resource_requirements"][resource_type] = 0
                    effects["resource_requirements"][resource_type] += license_cost
            
            elif law_type == "component_licensing" and action_type == "tech_development":
                # Check if this restricts the component being developed
                restricted_component = law.get("parameters", {}).get("UBER_TECH_COMPONENT")
                component_name = context.get("component_name")
                
                if restricted_component == component_name:
                    # Add licensing cost
                    license_cost = int(law.get("parameters", {}).get("LICENSE_COST", 0))
                    resource_type = law.get("parameters", {}).get("RESOURCE_TYPE")
                    
                    effects["license_cost"] += license_cost
                    if resource_type not in effects["resource_requirements"]:
                        effects["resource_requirements"][resource_type] = 0
                    effects["resource_requirements"][resource_type] += license_cost
            
            elif law_type == "chrono_shard_fee" and action_type == "chrono_shard_transaction":
                # Check if the transaction exceeds the threshold
                threshold = int(law.get("parameters", {}).get("THRESHOLD", 0))
                transaction_amount = context.get("amount", 0)
                
                if transaction_amount > threshold:
                    fee_percentage = float(law.get("parameters", {}).get("FEE_PERCENTAGE", 0))
                    effects["tax_percentage"] += fee_percentage
            
            elif law_type == "black_market_penalty" and action_type == "black_market":
                # Check if the operation is in the restricted region
                region = law.get("parameters", {}).get("REGION")
                operation_region = context.get("region")
                
                if region == operation_region or region == "ALL":
                    resource_type = law.get("parameters", {}).get("RESOURCE_TYPE")
                    penalty = int(law.get("parameters", {}).get("PENALTY", 0))
                    
                    if resource_type not in effects["resource_requirements"]:
                        effects["resource_requirements"][resource_type] = 0
                    effects["resource_requirements"][resource_type] += penalty
                    
                    effects["restrictions"].append({
                        "type": "black_market_penalty",
                        "region": region,
                        "penalty": penalty,
                        "resource_type": resource_type
                    })
            
            elif law_type == "project_tax" and action_type == "project_completion":
                # This applies to all Universal Projects
                tax_percentage = float(law.get("parameters", {}).get("TAX_PERCENTAGE", 0))
                effects["tax_percentage"] += tax_percentage
            
            elif law_type == "benefit_sharing" and action_type == "project_benefits":
                # Check if this is the project with forced benefit sharing
                project_name = law.get("parameters", {}).get("PROJECT_NAME")
                context_project = context.get("project_name")
                
                if project_name == context_project:
                    beneficiaries = law.get("parameters", {}).get("BENEFICIARIES", [])
                    duration = int(law.get("parameters", {}).get("DURATION", 0))
                    
                    effects["restrictions"].append({
                        "type": "benefit_sharing",
                        "project": project_name,
                        "beneficiaries": beneficiaries,
                        "duration": duration
                    })
        
        # Cap tax percentage at 100%
        effects["tax_percentage"] = min(effects["tax_percentage"], 100)
        
        return effects