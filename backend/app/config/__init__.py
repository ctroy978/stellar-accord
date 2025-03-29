# app/config/__init__.py
from app.config.manager import ConfigurationManager
from app.config.star_map import StarMapConfig
from app.config.trade import TradeConfig

# Initialize the configuration manager
config_manager = ConfigurationManager()

# Register configuration types
config_manager.register_config_class("star_map", StarMapConfig)
config_manager.register_config_class("trade", TradeConfig)

# Do not initialize with defaults here - we'll do this in a controlled way
# config_manager.reset_to_defaults("star_map")
# config_manager.reset_to_defaults("trade")

def get_config_manager() -> ConfigurationManager:
    """Get the global configuration manager instance."""
    return config_manager

def initialize_configurations():
    """Initialize configurations with defaults."""
    config_manager.reset_to_defaults("star_map")
    config_manager.reset_to_defaults("trade")