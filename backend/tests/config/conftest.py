# tests/config/conftest.py
import pytest
from app.config import get_config_manager, initialize_configurations

@pytest.fixture(scope="session", autouse=True)
def initialize_config():
    """Initialize configurations for tests."""
    config_manager = get_config_manager()
    
    # Clear any existing configurations
    config_manager._configs = {}
    
    # Initialize with defaults
    initialize_configurations()
    
    return config_manager