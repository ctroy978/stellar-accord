# app/config/tech_rules.py
from typing import Dict, List, Any, Optional
from uuid import UUID
from app.config.base import BaseConfiguration

class TechComponent:
    """Represents a technology component in the game."""
    
    def __init__(self, component_id: str, name: str, description: str,
                 tech_type: str, tech_group: Optional[str] = None):
        self.component_id = component_id
        self.name = name
        self.description = description
        self.tech_type = tech_type  # 'big_tech', 'uber_tech', etc.
        self.tech_group = tech_group  # Used for grouping (e.g., 'A', 'B', etc.)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "component_id": self.component_id,
            "name": self.name,
            "description": self.description,
            "tech_type": self.tech_type,
            "tech_group": self.tech_group
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TechComponent':
        """Create from dictionary."""
        return cls(
            component_id=data["component_id"],
            name=data["name"],
            description=data.get("description", ""),
            tech_type=data["tech_type"],
            tech_group=data.get("tech_group")
        )

class TechRequirement:
    """Represents a requirement for a technology component."""
    
    def __init__(self, required_id: str, required_type: str, quantity: int = 1):
        self.required_id = required_id
        self.required_type = required_type  # 'resource', 'big_tech', etc.
        self.quantity = quantity
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "required_id": self.required_id,
            "required_type": self.required_type,
            "quantity": self.quantity
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TechRequirement':
        """Create from dictionary."""
        return cls(
            required_id=data["required_id"],
            required_type=data["required_type"],
            quantity=data.get("quantity", 1)
        )

class TechnologyConfig(BaseConfiguration):
    """Configuration for technology components and their requirements."""
    
    def __init__(self, config_id: Optional[UUID] = None):
        super().__init__(config_id)
        self.components = {}  # component_id -> TechComponent
        self.requirements = {}  # component_id -> [TechRequirement]
        self.civilization_capabilities = {}  # civilization_id -> [tech_group]
        self._load_defaults()
    
    def _load_defaults(self):
        """Load default technology configuration."""
        defaults = self.get_defaults()
        
        # Load components
        for component_data in defaults.get("components", []):
            component = TechComponent.from_dict(component_data)
            self.components[component.component_id] = component
        
        # Load requirements
        for component_id, requirements_data in defaults.get("requirements", {}).items():
            self.requirements[component_id] = [
                TechRequirement.from_dict(req_data) for req_data in requirements_data
            ]
        
        # Load civilization capabilities
        self.civilization_capabilities = defaults.get("civilization_capabilities", {})
    
    def get_defaults(self) -> Dict[str, Any]:
        """Return default configuration values."""
        # Pull from your design document for these defaults
        return {
            "components": [
                # Sample Big Tech components
                {
                    "component_id": "power_conversion_system",
                    "name": "Power Conversion System",
                    "description": "Fundamental system for transforming energy between forms",
                    "tech_type": "big_tech",
                    "tech_group": "A"
                },
                # Add more components here
            ],
            "requirements": {
                # Sample requirements for a Big Tech component
                "power_conversion_system": [
                    {
                        "required_id": "neutronium",
                        "required_type": "resource",
                        "quantity": 30
                    },
                    {
                        "required_id": "photon_crystal",
                        "required_type": "resource",
                        "quantity": 25
                    },
                    {
                        "required_id": "living_metal",
                        "required_type": "resource",
                        "quantity": 15
                    }
                ],
                # Add more requirements here
            },
            "civilization_capabilities": {
                # Define which tech groups each civilization can develop
                "Thrizoth": ["A", "B", "C", "D", "E"],
                "Methane Collective": ["A", "B", "C", "D", "F"],
                "Silicon Liberation": ["A", "B", "C", "D"],
                "Glacian Current": ["A", "B", "C", "E"],
                "Kyrathi": ["A", "B", "C", "E"],
                "Vasku": ["A", "B", "C", "F"]
            }
        }
    
    def validate(self) -> bool:
        """Validate the configuration."""
        # Validate components exist
        if not self.components:
            return False
        
        # Validate requirements reference valid components and resources
        for component_id, requirements in self.requirements.items():
            if component_id not in self.components:
                return False
            
            for requirement in requirements:
                if requirement.required_type == "big_tech" and requirement.required_id not in self.components:
                    return False
                # Note: Resource validation would require a reference to resource config
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        data = super().to_dict()
        data.update({
            "components": [component.to_dict() for component in self.components.values()],
            "requirements": {
                component_id: [req.to_dict() for req in requirements]
                for component_id, requirements in self.requirements.items()
            },
            "civilization_capabilities": self.civilization_capabilities
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TechnologyConfig':
        """Create configuration from dictionary."""
        config = super(TechnologyConfig, cls).from_dict(data)
        
        # Clear defaults
        config.components = {}
        config.requirements = {}
        
        # Load components
        for component_data in data.get("components", []):
            component = TechComponent.from_dict(component_data)
            config.components[component.component_id] = component
        
        # Load requirements
        for component_id, requirements_data in data.get("requirements", {}).items():
            config.requirements[component_id] = [
                TechRequirement.from_dict(req_data) for req_data in requirements_data
            ]
        
        # Load civilization capabilities
        config.civilization_capabilities = data.get("civilization_capabilities", {})
        
        return config
    
    def can_civilization_develop(self, civilization_id: str, component_id: str) -> bool:
        """Check if a civilization can develop a specific technology component."""
        if component_id not in self.components:
            return False
            
        component = self.components[component_id]
        if not component.tech_group:
            return True  # Universal tech with no group restriction
            
        allowed_groups = self.civilization_capabilities.get(civilization_id, [])
        return component.tech_group in allowed_groups
    
    def get_development_requirements(self, component_id: str) -> List[TechRequirement]:
        """Get all requirements for developing a technology component."""
        return self.requirements.get(component_id, [])
    