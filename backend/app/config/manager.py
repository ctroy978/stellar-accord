# app/config/manager.py
from typing import Dict, Type, Optional, Any
import json
from uuid import UUID
import os

from app.config.base import BaseConfiguration

class ConfigurationManager:
    """Singleton manager for all configuration modules."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigurationManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._configs = {}
        self._config_classes = {}
        self._initialized = True
    
    def register_config_class(self, config_type: str, config_class: Type[BaseConfiguration]):
        """Register a configuration class for a specific type."""
        self._config_classes[config_type] = config_class
    
    def get_config(self, config_type: str) -> Optional[BaseConfiguration]:
        """Get the active configuration for a specific type."""
        return self._configs.get(config_type)
    
    def set_config(self, config_type: str, config: BaseConfiguration):
        """Set the active configuration for a specific type."""
        if not config.validate():
            raise ValueError(f"Invalid configuration for {config_type}")
        self._configs[config_type] = config
    
    def load_from_dict(self, config_type: str, data: Dict[str, Any]) -> BaseConfiguration:
        """Load configuration from dictionary."""
        if config_type not in self._config_classes:
            raise ValueError(f"Unknown configuration type: {config_type}")
            
        config_class = self._config_classes[config_type]
        config = config_class.from_dict(data)
        self.set_config(config_type, config)
        return config
    
    def load_from_json(self, config_type: str, json_str: str) -> BaseConfiguration:
        """Load configuration from JSON string."""
        return self.load_from_dict(config_type, json.loads(json_str))
    
    def load_from_file(self, config_type: str, file_path: str) -> BaseConfiguration:
        """Load configuration from JSON file."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
            
        with open(file_path, 'r') as f:
            return self.load_from_json(config_type, f.read())
    
    def save_to_file(self, config_type: str, file_path: str):
        """Save configuration to JSON file."""
        config = self.get_config(config_type)
        if not config:
            raise ValueError(f"No configuration found for {config_type}")
            
        with open(file_path, 'w') as f:
            f.write(config.to_json())
    
    def reset_to_defaults(self, config_type: str) -> BaseConfiguration:
        """Reset configuration to its defaults."""
        if config_type not in self._config_classes:
            raise ValueError(f"Unknown configuration type: {config_type}")
            
        config_class = self._config_classes[config_type]
        config = config_class()  # Create a new instance with defaults
        self.set_config(config_type, config)
        return config