# app/config/__init__.py
from app.config.manager import ConfigurationManager
from app.config.star_map import StarMapConfig
from app.config.trade import TradeConfig
from app.config.technology import TechnologyConfig
from app.config.game_rules import GameRulesConfig
from app.config.law_system import LawSystemConfig
from app.config.intel_operations import IntelOperationsConfig

# Initialize the configuration manager
config_manager = ConfigurationManager()

# Register all configuration classes
config_manager.register_config_class("star_map", StarMapConfig)
config_manager.register_config_class("trade", TradeConfig)
config_manager.register_config_class("technology", TechnologyConfig)
config_manager.register_config_class("game_rules", GameRulesConfig)
config_manager.register_config_class("law_system", LawSystemConfig)
config_manager.register_config_class("intel_operations", IntelOperationsConfig)

def get_config_manager() -> ConfigurationManager:
    """Get the global configuration manager instance."""
    return config_manager

def initialize_configurations():
    """Initialize configurations with defaults."""
    config_manager.reset_to_defaults("star_map")
    config_manager.reset_to_defaults("trade")
    config_manager.reset_to_defaults("technology")
    config_manager.reset_to_defaults("game_rules")
    config_manager.reset_to_defaults("law_system")
    config_manager.reset_to_defaults("intel_operations")





