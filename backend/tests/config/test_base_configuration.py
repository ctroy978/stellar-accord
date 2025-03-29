# tests/config/test_base_configuration.py
import pytest
import uuid
from datetime import datetime
from app.config.base import BaseConfiguration

class TestConfiguration(BaseConfiguration):
    """Test implementation of BaseConfiguration for testing."""
    
    def get_defaults(self):
        return {"test_value": 123}
    
    def validate(self):
        return True

class TestBaseConfiguration:
    def test_init(self):
        """Test initialization with defaults."""
        config = TestConfiguration()
        assert config.config_id is not None
        assert config.version == 1
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        config = TestConfiguration()
        data = config.to_dict()
        assert "config_id" in data
        assert data["version"] == 1
    
    def test_from_dict(self):
        """Test creation from dictionary."""
        test_id = uuid.uuid4()
        data = {
            "config_id": str(test_id),
            "version": 2,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "description": "Test config"
        }
        
        config = TestConfiguration.from_dict(data)
        assert config.config_id == test_id
        assert config.version == 2
        assert config.description == "Test config"