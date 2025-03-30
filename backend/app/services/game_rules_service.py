# app/services/game_rules_service.py
from typing import Dict, List, Optional, Any
from uuid import UUID

from app.config.utils import get_game_rules_config

class GameRulesService:
    """
    Service for game rule operations using the configuration system.
    
    This service provides methods that leverage game rules configuration to 
    implement game mechanics related to phases, communication, laws, and intelligence.
    """
    
    @staticmethod
    def get_round_structure() -> List[str]:
        """
        Get the round structure (sequence of phases).
        
        Returns:
            List of phase names in order
        """
        rules_config = get_game_rules_config()
        return rules_config.round_structure
    
    @staticmethod
    def get_phase_timing(phase: Optional[str] = None) -> Dict[str, int]:
        """
        Get the duration for a specific phase or all phases.
        
        Args:
            phase: Optional specific phase to get timing for
            
        Returns:
            Dictionary of phase durations or single duration
        """
        rules_config = get_game_rules_config()
        
        if phase:
            return {phase: rules_config.get_phase_duration(phase)}
        else:
            return rules_config.phase_durations
    
    @staticmethod
    def advance_phase(current_phase: str) -> Dict[str, Any]:
        """
        Determine the next phase in the game sequence.
        
        Args:
            current_phase: The current phase
            
        Returns:
            Dictionary with next phase information
        """
        rules_config = get_game_rules_config()
        
        next_phase = rules_config.get_next_phase(current_phase)
        is_new_round = rules_config.is_last_phase_in_round(current_phase)
        
        return {
            "current_phase": current_phase,
            "next_phase": next_phase,
            "new_round_starting": is_new_round,
            "phase_duration": rules_config.get_phase_duration(next_phase)
        }
    
    @staticmethod
    def check_communication_allowed(civ1: str, civ2: str) -> Dict[str, Any]:
        """
        Check if two civilizations can communicate directly.
        
        Args:
            civ1: First civilization name
            civ2: Second civilization name
            
        Returns:
            Dictionary with communication status
        """
        rules_config = get_game_rules_config()
        
        can_communicate = rules_config.can_civilizations_communicate(civ1, civ2)
        
        result = {
            "can_communicate": can_communicate,
            "civilizations": [civ1, civ2]
        }
        
        if not can_communicate:
            # Check which civilization(s) have the restriction
            if (civ1 in rules_config.communication_restrictions and 
                civ2 in rules_config.communication_restrictions[civ1]):
                result["restriction_source"] = civ1
            
            if (civ2 in rules_config.communication_restrictions and 
                civ1 in rules_config.communication_restrictions[civ2]):
                if "restriction_source" in result:
                    result["restriction_source"] = "both"
                else:
                    result["restriction_source"] = civ2
        
        return result
    
    @staticmethod
    def get_law_constraints() -> Dict[str, int]:
        """
        Get constraints for the law system.
        
        Returns:
            Dictionary with law system parameters
        """
        rules_config = get_game_rules_config()
        
        return {
            "law_duration": rules_config.law_duration,
            "max_active_laws": rules_config.max_active_laws
        }
    
    @staticmethod
    def calculate_trade_costs(distance_jumps: int) -> Dict[str, float]:
        """
        Calculate trade costs based on distance.
        
        Args:
            distance_jumps: Number of star gate jumps between systems
            
        Returns:
            Dictionary with cost calculations
        """
        rules_config = get_game_rules_config()
        trade_rules = rules_config.trading_rules
        
        # Calculate base cost
        base_cost = distance_jumps * trade_rules.get("base_delivery_cost_percentage", 5.0)
        
        # Apply min/max constraints
        min_cost = trade_rules.get("min_delivery_cost_percentage", 10.0)
        max_cost = trade_rules.get("max_delivery_cost_percentage", 30.0)
        
        final_cost = max(min_cost, min(base_cost, max_cost))
        
        return {
            "distance_jumps": distance_jumps,
            "base_rate_per_jump": trade_rules.get("base_delivery_cost_percentage", 5.0),
            "base_cost": base_cost,
            "minimum_cost": min_cost,
            "maximum_cost": max_cost,
            "final_cost_percentage": final_cost
        }
    
    @staticmethod
    def calculate_counterfeit_success(catalyst_quantity: int) -> Dict[str, Any]:
        """
        Calculate success chance for counterfeiting operations.
        
        Args:
            catalyst_quantity: Quantity of catalyst material used
            
        Returns:
            Dictionary with counterfeit operation details
        """
        rules_config = get_game_rules_config()
        trade_rules = rules_config.trading_rules
        
        base_rate = trade_rules.get("counterfeit_success_base_rate", 50.0)
        max_rate = trade_rules.get("counterfeit_success_max_rate", 75.0)
        
        # Additional success per catalyst unit (each 1 unit = +1%)
        additional_success = min(catalyst_quantity, int(max_rate - base_rate))
        final_success_rate = base_rate + additional_success
        
        return {
            "base_success_rate": base_rate,
            "catalyst_quantity": catalyst_quantity,
            "additional_success_rate": additional_success,
            "final_success_rate": final_success_rate,
            "conversion_ratio": trade_rules.get("counterfeit_conversion_ratio", 5)
        }
    
    @staticmethod
    def calculate_intelligence_operation(operation_name: str, 
                                       resource_investment: Dict[str, int]) -> Dict[str, Any]:
        """
        Calculate success chance and costs for an intelligence operation.
        
        Args:
            operation_name: Name of the operation
            resource_investment: Dictionary of resources being invested
            
        Returns:
            Dictionary with operation details
        """
        rules_config = get_game_rules_config()
        
        # Find the operation definition
        operation = None
        for op in rules_config.intelligence_operation_rules.get("universal_operations", []):
            if op["name"] == operation_name:
                operation = op
                break
        
        if not operation:
            return {
                "success": False,
                "error": "Operation not found",
                "details": {"operation_name": operation_name}
            }
        
        # Calculate success rate
        success_rate = rules_config.calculate_intelligence_success_rate(
            operation_name, resource_investment
        )
        
        # Check if base costs are met
        base_cost = operation.get("base_cost", {})
        missing_resources = []
        
        for resource, quantity in base_cost.items():
            if resource not in resource_investment or resource_investment[resource] < quantity:
                missing_resources.append({
                    "resource": resource,
                    "required": quantity,
                    "provided": resource_investment.get(resource, 0)
                })
        
        if missing_resources:
            return {
                "success": False,
                "error": "Insufficient resources for operation",
                "missing_resources": missing_resources
            }
        
        return {
            "success": True,
            "operation_name": operation_name,
            "base_success_rate": operation.get("base_success_rate", 0.0),
            "final_success_rate": success_rate,
            "resource_investment": resource_investment,
            "base_cost": base_cost
        }