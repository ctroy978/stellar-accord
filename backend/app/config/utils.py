# app/config/utils.py
"""
Configuration Utility Functions

This module provides utility functions for accessing and working with 
game configurations. These functions serve as convenient access points
to retrieve properly initialized configuration objects and to perform
common operations that rely on multiple configuration systems.
"""

from typing import Optional, List, Dict, Tuple
from app.config import get_config_manager
from app.config.star_map import StarMapConfig
from app.config.trade import TradeConfig
from app.config.tech_rules import TechnologyConfig
from app.config.game_rules import GameRulesConfig
from app.config.law_system import LawSystemConfig
from app.config.intel_operations import IntelOperationsConfig




def get_star_map_config() -> StarMapConfig:
    """
    Get the current star map configuration.
    
    This function ensures that a properly initialized map configuration
    is available, creating one with defaults if necessary.
    
    Returns:
        The current StarMapConfig instance
    """
    config_manager = get_config_manager()
    
    # Ensure the configuration type is registered
    if "star_map" not in config_manager._config_classes:
        from app.config.star_map import StarMapConfig
        config_manager.register_config_class("star_map", StarMapConfig)
    
    config = config_manager.get_config("star_map")
    
    # Initialize if not already present
    if config is None:
        config = StarMapConfig()
        # Don't use reset_to_defaults which would call validate before initialization
        config_manager._configs["star_map"] = config
        
    return config

def get_trade_config() -> TradeConfig:
    """
    Get the current trade configuration.
    
    This function ensures that a properly initialized trade configuration
    is available, creating one with defaults if necessary.
    
    Returns:
        The current TradeConfig instance
    """
    config_manager = get_config_manager()
    
    # Ensure the configuration type is registered
    if "trade" not in config_manager._config_classes:
        from app.config.trade import TradeConfig
        config_manager.register_config_class("trade", TradeConfig)
    
    config = config_manager.get_config("trade")
    
    # Initialize if not already present
    if config is None:
        config = config_manager.reset_to_defaults("trade")
        
    return config

def calculate_delivery_cost(civ_system_id: str, hub_id: str) -> float:
    """
    Calculate delivery cost between a civilization's system and a hub.
    
    This function combines spatial data from the star map with trade rules
    to calculate the delivery cost percentage for a given route.
    
    Args:
        civ_system_id: The system ID of the civilization
        hub_id: The ID of the hub
        
    Returns:
        Delivery cost as a percentage
    """
    star_map = get_star_map_config()
    trade_config = get_trade_config()
    
    # Calculate jumps using star map
    jumps = star_map.calculate_jumps(civ_system_id, hub_id)
    
    if jumps < 0:
        # No valid path
        return trade_config.max_delivery_cost_percentage
    
    # Apply trade rules to the spatial data
    return trade_config.calculate_delivery_cost(jumps, hub_id)

def get_hub_distance_table() -> Dict[str, Dict[str, Tuple[int, float]]]:
    """
    Get a table of jumps and delivery costs for all civilizations and hubs.
    
    This function integrates the star map and trade configuration systems
    to build a comprehensive table of distances and costs, which is useful
    for display purposes and for making trade decisions.
    
    Returns a dictionary mapping:
    civilization_id -> {
        hub_id -> (jumps, cost_percentage)
    }
    """
    star_map = get_star_map_config()
    trade_config = get_trade_config()
    
    # Create a default result in case of configuration issues
    default_result = {
        "Thrizoth": {
            "Alpha": (1, 10.0),
            "Beta": (2, 15.0),
            "Gamma": (3, 20.0)
        },
        "Methane Collective": {
            "Alpha": (3, 20.0),
            "Beta": (2, 15.0),
            "Gamma": (1, 10.0)
        },
        "Silicon Liberation": {
            "Alpha": (1, 10.0),
            "Beta": (1, 10.0),
            "Gamma": (3, 20.0)
        },
        "Glacian Current": {
            "Alpha": (3, 20.0),
            "Beta": (2, 15.0),
            "Gamma": (1, 10.0)
        },
        "Kyrathi": {
            "Alpha": (1, 10.0),
            "Beta": (1, 10.0),
            "Gamma": (3, 20.0)
        },
        "Vasku": {
            "Alpha": (3, 20.0),
            "Beta": (1, 10.0),
            "Gamma": (2, 15.0)
        }
    }
    
    # If configuration is not properly initialized, return default
    if star_map is None or not hasattr(star_map, 'systems'):
        return default_result
        
    # Attempt to build the real table from configuration
    try:
        # Get all civilization systems and hub systems
        civ_systems = {system.civilization_id: system for system in star_map.systems.values() 
                      if system.civilization_id}
        hub_systems = [system for system in star_map.systems.values() if system.is_hub]
        
        # Calculate jumps and costs for each civilization-hub pair
        result = {}
        for civ_id, system in civ_systems.items():
            result[civ_id] = {}
            for hub in hub_systems:
                jumps = star_map.calculate_jumps(system.system_id, hub.system_id)
                cost = trade_config.calculate_delivery_cost(jumps if jumps >= 0 else 999, hub.system_id)
                result[civ_id][hub.system_id] = (jumps, cost)
        
        return result
    except Exception:
        # If anything fails, fall back to defaults
        return default_result


def get_technology_config() -> TechnologyConfig:
    """
    Get the current technology configuration.
    
    This function ensures that a properly initialized technology configuration
    is available, creating one with defaults if necessary.
    
    Returns:
        The current TechnologyConfig instance
    """
    config_manager = get_config_manager()
    
    # Ensure the configuration type is registered
    if "technology" not in config_manager._config_classes:
        from app.config.technology import TechnologyConfig
        config_manager.register_config_class("technology", TechnologyConfig)
    
    config = config_manager.get_config("technology")
    
    # Initialize if not already present
    if config is None:
        config = config_manager.reset_to_defaults("technology")
        
    return config

def get_game_rules_config() -> GameRulesConfig:
    """
    Get the current game rules configuration.
    
    This function ensures that a properly initialized game rules configuration
    is available, creating one with defaults if necessary.
    
    Returns:
        The current GameRulesConfig instance
    """
    config_manager = get_config_manager()
    
    # Ensure the configuration type is registered
    if "game_rules" not in config_manager._config_classes:
        from app.config.game_rules import GameRulesConfig
        config_manager.register_config_class("game_rules", GameRulesConfig)
    
    config = config_manager.get_config("game_rules")
    
    # Initialize if not already present
    if config is None:
        config = config_manager.reset_to_defaults("game_rules")
        
    return config


def get_law_system_config() -> 'LawSystemConfig':
    """
    Get the current law system configuration.
    
    This function ensures that a properly initialized law system configuration
    is available, creating one with defaults if necessary.
    
    Returns:
        The current LawSystemConfig instance
    """
    config_manager = get_config_manager()
    
    # Ensure the configuration type is registered
    if "law_system" not in config_manager._config_classes:
        from app.config.law_system import LawSystemConfig
        config_manager.register_config_class("law_system", LawSystemConfig)
    
    config = config_manager.get_config("law_system")
    
    # Initialize if not already present
    if config is None:
        config = config_manager.reset_to_defaults("law_system")
        
    return config



def get_intel_operations_config() -> 'IntelOperationsConfig':
    """
    Get the current intelligence operations configuration.
    
    This function ensures that a properly initialized intel operations configuration
    is available, creating one with defaults if necessary.
    
    Returns:
        The current IntelOperationsConfig instance
    """
    config_manager = get_config_manager()
    
    # Ensure the configuration type is registered
    if "intel_operations" not in config_manager._config_classes:
        from app.config.intel_operations import IntelOperationsConfig
        config_manager.register_config_class("intel_operations", IntelOperationsConfig)
    
    config = config_manager.get_config("intel_operations")
    
    # Initialize if not already present
    if config is None:
        config = config_manager.reset_to_defaults("intel_operations")
        
    return config


def get_intel_operations_config() -> IntelOperationsConfig:
    """
    Get the current intelligence operations configuration.
    
    This function ensures that a properly initialized intel operations configuration
    is available, creating one with defaults if necessary.
    
    Returns:
        The current IntelOperationsConfig instance
    """
    config_manager = get_config_manager()
    
    # Ensure the configuration type is registered
    if "intel_operations" not in config_manager._config_classes:
        from app.config.intel_operations import IntelOperationsConfig
        config_manager.register_config_class("intel_operations", IntelOperationsConfig)
    
    config = config_manager.get_config("intel_operations")
    
    # Initialize if not already present
    if config is None:
        config = config_manager.reset_to_defaults("intel_operations")
        
    return config

def get_intel_operations_config() -> 'IntelOperationsConfig':
    """
    Get the current intelligence operations configuration.
    
    This function ensures that a properly initialized intel operations configuration
    is available, creating one with defaults if necessary.
    
    Returns:
        The current IntelOperationsConfig instance
    """
    config_manager = get_config_manager()
    
    # Ensure the configuration type is registered
    if "intel_operations" not in config_manager._config_classes:
        from app.config.intel_operations import IntelOperationsConfig
        config_manager.register_config_class("intel_operations", IntelOperationsConfig)
    
    config = config_manager.get_config("intel_operations")
    
    # Initialize if not already present
    if config is None:
        config = config_manager.reset_to_defaults("intel_operations")
        
    return config