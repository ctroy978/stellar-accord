# tests/config/test_config_manager.py
import pytest
import uuid
import os
import tempfile
from app.config.manager import ConfigurationManager
from app.config.star_map import StarMapConfig
from app.config.trade import TradeConfig

class TestConfigurationManager:
    def test_singleton_pattern(self):
        """Test that manager is a singleton."""
        manager1 = ConfigurationManager()
        manager2 = ConfigurationManager()
        assert manager1 is manager2
    
    def test_register_config_class(self):
        """Test registering configuration classes."""
        manager = ConfigurationManager()
        manager._config_classes = {}  # Reset for test
        
        manager.register_config_class("test", StarMapConfig)
        assert "test" in manager._config_classes
        assert manager._config_classes["test"] == StarMapConfig
    
    def test_set_and_get_config(self):
        """Test setting and getting configurations."""
        manager = ConfigurationManager()
        manager._configs = {}  # Reset for test
        
        config = StarMapConfig()
        manager.set_config("star_map", config)
        
        retrieved_config = manager.get_config("star_map")
        assert retrieved_config is config
    

    def test_load_from_dict(self):
        """Test loading configuration from dictionary."""
        manager = ConfigurationManager()
        manager._config_classes = {}  # Reset for test
        manager._configs = {}  # Reset for test
        
        manager.register_config_class("star_map", StarMapConfig)
        
        # Minimal valid data with at least one system
        data = {
            "config_id": str(uuid.uuid4()),
            "version": 1,
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00",
            "systems": [
                {
                    "system_id": "TEST",
                    "name": "Test System",
                    "position": (100, 100)
                }
            ],
            "connections": {"TEST": []}
        }
        
        config = manager.load_from_dict("star_map", data)
        assert isinstance(config, StarMapConfig)
        assert manager.get_config("star_map") is config
    
    def test_reset_to_defaults(self):
        """Test resetting to defaults."""
        manager = ConfigurationManager()
        manager._config_classes = {}  # Reset for test
        manager._configs = {}  # Reset for test
        
        manager.register_config_class("trade", TradeConfig)
        
        # Create non-default config
        config = TradeConfig()
        config.base_delivery_cost_percentage = 10.0  # Different from default
        manager.set_config("trade", config)
        
        # Reset to defaults
        new_config = manager.reset_to_defaults("trade")
        assert new_config.base_delivery_cost_percentage == 5.0  # Default value
    
    def test_file_operations(self):
        """Test saving and loading from file."""
        manager = ConfigurationManager()
        manager._config_classes = {}  # Reset for test
        manager._configs = {}  # Reset for test
        
        manager.register_config_class("trade", TradeConfig)
        original_config = TradeConfig()
        original_config.base_delivery_cost_percentage = 15.0
        manager.set_config("trade", original_config)
        
        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # Save to file
            manager.save_to_file("trade", tmp_path)
            
            # Reset manager
            manager._configs = {}
            
            # Load from file
            loaded_config = manager.load_from_file("trade", tmp_path)
            assert loaded_config.base_delivery_cost_percentage == 15.0
        finally:
            # Clean up
            os.unlink(tmp_path)