# app/config/base.py
from abc import ABC, abstractmethod
import json
from typing import Dict, Any, Optional
from uuid import UUID, uuid4
from datetime import datetime

class BaseConfiguration(ABC):
    """Abstract base class for all configuration modules."""
    
    def __init__(self, config_id: Optional[UUID] = None):
        self.config_id = config_id or uuid4()
        self.version = 1
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.description = ""
        
    @abstractmethod
    def get_defaults(self) -> Dict[str, Any]:
        """Return default configuration values."""
        pass
        
    @abstractmethod
    def validate(self) -> bool:
        """Validate the configuration is correct and complete."""
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "config_id": str(self.config_id),
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "description": self.description,
            # Child classes should implement their own to_dict and call super().to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseConfiguration':
        """Create configuration from dictionary."""
        instance = cls(config_id=UUID(data.get("config_id")))
        instance.version = data.get("version", 1)
        instance.created_at = datetime.fromisoformat(data.get("created_at"))
        instance.updated_at = datetime.fromisoformat(data.get("updated_at"))
        instance.description = data.get("description", "")
        return instance
    
    def to_json(self) -> str:
        """Convert configuration to JSON string."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str) -> 'BaseConfiguration':
        """Create configuration from JSON string."""
        return cls.from_dict(json.loads(json_str))