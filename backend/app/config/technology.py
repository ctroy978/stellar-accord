# app/config/technology.py
from typing import Dict, List, Any, Optional, Set
from uuid import UUID
from app.config.base import BaseConfiguration

class TechComponent:
    """Represents a technology component in the game."""
    
    def __init__(self, component_id: str, name: str, description: str,
                 tech_type: str, tech_group: Optional[str] = None,
                 civilization_restrictions: Optional[List[str]] = None):
        self.component_id = component_id
        self.name = name
        self.description = description
        self.tech_type = tech_type  # 'big_tech', 'uber_tech', 'universal_project'
        self.tech_group = tech_group  # Used for grouping (e.g., 'A', 'B', etc.)
        self.civilization_restrictions = civilization_restrictions or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "component_id": self.component_id,
            "name": self.name,
            "description": self.description,
            "tech_type": self.tech_type,
            "tech_group": self.tech_group,
            "civilization_restrictions": self.civilization_restrictions
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TechComponent':
        """Create from dictionary."""
        return cls(
            component_id=data["component_id"],
            name=data["name"],
            description=data.get("description", ""),
            tech_type=data["tech_type"],
            tech_group=data.get("tech_group"),
            civilization_restrictions=data.get("civilization_restrictions", [])
        )


class TechRequirement:
    """Represents a requirement for a technology component."""
    
    def __init__(self, required_id: str, required_type: str, quantity: int = 1):
        self.required_id = required_id
        self.required_type = required_type  # 'resource', 'big_tech', 'uber_tech'
        self.quantity = max(1, quantity)  # Ensure quantity is at least 1
    
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
        self.project_effects = {}  # project_id -> Dict of effects
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
        
        # Load project effects
        self.project_effects = defaults.get("project_effects", {})
    
    def get_defaults(self) -> Dict[str, Any]:
        """Return default configuration values."""
        return {
            "components": [
                # Big Tech Components - Group A
                {
                    "component_id": "power_conversion_system",
                    "name": "Power Conversion System",
                    "description": "Fundamental system for transforming energy between forms",
                    "tech_type": "big_tech",
                    "tech_group": "A"
                },
                {
                    "component_id": "energy_amplification_array",
                    "name": "Energy Amplification Array",
                    "description": "System for enhancing energy output efficiency",
                    "tech_type": "big_tech",
                    "tech_group": "A"
                },
                {
                    "component_id": "directional_flow_controller",
                    "name": "Directional Flow Controller",
                    "description": "Controls the movement and direction of energy streams",
                    "tech_type": "big_tech",
                    "tech_group": "A"
                },
                {
                    "component_id": "containment_field_generator",
                    "name": "Containment Field Generator",
                    "description": "Creates stable fields to contain unstable energy and matter",
                    "tech_type": "big_tech",
                    "tech_group": "A"
                },
                {
                    "component_id": "wave_harmonization_grid",
                    "name": "Wave Harmonization Grid",
                    "description": "Synchronizes energy waves to prevent interference patterns",
                    "tech_type": "big_tech",
                    "tech_group": "A"
                },
                  {
                "component_id": "structural_integrity_field",
                "name": "Structural Integrity Field",
                "description": "System for reinforcing and stabilizing physical constructs",
                "tech_type": "uber_tech"
                },
                # These might also be needed based on the dyson_sphere requirements
                {
                    "component_id": "thermal_regulation_network",
                    "name": "Thermal Regulation Network",
                    "description": "Technology for controlling heat and energy distribution",
                    "tech_type": "uber_tech"
                },
                {
                    "component_id": "stellar_manipulation_array",
                    "name": "Stellar Manipulation Array",
                    "description": "Technology for controlling and modifying stars",
                    "tech_type": "uber_tech"
                },
                
                # Big Tech Components - Group B
                {
                    "component_id": "quantum_calculation_engine",
                    "name": "Quantum Calculation Engine",
                    "description": "Performs calculations using quantum superposition",
                    "tech_type": "big_tech",
                    "tech_group": "B"
                },
                {
                    "component_id": "particle_pairing_system",
                    "name": "Particle Pairing System",
                    "description": "Creates and maintains quantum entanglement between particles",
                    "tech_type": "big_tech",
                    "tech_group": "B"
                },
                {
                    "component_id": "coherence_maintenance_field",
                    "name": "Coherence Maintenance Field",
                    "description": "Prevents quantum decoherence in sensitive systems",
                    "tech_type": "big_tech",
                    "tech_group": "B"
                },
                {
                    "component_id": "instantaneous_transfer_protocol",
                    "name": "Instantaneous Transfer Protocol",
                    "description": "Enables faster-than-light information transfer through quantum channels",
                    "tech_type": "big_tech",
                    "tech_group": "B"
                },
                {
                    "component_id": "quantum_state_observer",
                    "name": "Quantum State Observer",
                    "description": "Monitors and records quantum states without causing collapse",
                    "tech_type": "big_tech",
                    "tech_group": "B"
                },
                
                # Sample Uber Tech components
                {
                    "component_id": "energy_manipulation_matrix",
                    "name": "Energy Manipulation Matrix",
                    "description": "Fundamental system for controlling and transforming energy",
                    "tech_type": "uber_tech"
                },
                {
                    "component_id": "quantum_entanglement_network",
                    "name": "Quantum Entanglement Network",
                    "description": "Framework for instantaneous connections across space",
                    "tech_type": "uber_tech"
                },
                {
                    "component_id": "gravitational_control_system",
                    "name": "Gravitational Control System",
                    "description": "Technology to manipulate gravity and spacetime",
                    "tech_type": "uber_tech"
                },
                
                # Sample Universal Projects
                {
                    "component_id": "dyson_sphere",
                    "name": "Dyson Sphere",
                    "description": "A megastructure surrounding a star to capture nearly 100% of its energy output",
                    "tech_type": "universal_project"
                },
                {
                    "component_id": "galactic_wormhole_network",
                    "name": "Galactic Wormhole Network",
                    "description": "A system of artificial wormholes connecting key points across the sector",
                    "tech_type": "universal_project"
                },
                {
                    "component_id": "quantum_consciousness_grid",
                    "name": "Quantum Consciousness Grid",
                    "description": "A sector-wide quantum network enabling instantaneous communication and consciousness sharing",
                    "tech_type": "universal_project"
                }
            ],
            
            "requirements": {
                # Sample requirements for Big Tech components
                "power_conversion_system": [
                    {"required_id": "neutronium", "required_type": "resource", "quantity": 30},
                    {"required_id": "photon_crystal", "required_type": "resource", "quantity": 25},
                    {"required_id": "living_metal", "required_type": "resource", "quantity": 15}
                ],
                "energy_amplification_array": [
                    {"required_id": "solar_essence", "required_type": "resource", "quantity": 30},
                    {"required_id": "echo_crystal", "required_type": "resource", "quantity": 20},
                    {"required_id": "stellar_core_fragment", "required_type": "resource", "quantity": 10}
                ],
                
                # Sample requirements for Uber Tech components
                "energy_manipulation_matrix": [
                    {"required_id": "power_conversion_system", "required_type": "big_tech", "quantity": 1},
                    {"required_id": "energy_amplification_array", "required_type": "big_tech", "quantity": 1},
                    {"required_id": "directional_flow_controller", "required_type": "big_tech", "quantity": 1},
                    {"required_id": "containment_field_generator", "required_type": "big_tech", "quantity": 1},
                    {"required_id": "wave_harmonization_grid", "required_type": "big_tech", "quantity": 1},
                    {"required_id": "quantum_calculation_engine", "required_type": "big_tech", "quantity": 1}
                ],
                
                # Sample requirements for Universal Projects
                "dyson_sphere": [
                    {"required_id": "energy_manipulation_matrix", "required_type": "uber_tech", "quantity": 1},
                    {"required_id": "structural_integrity_field", "required_type": "uber_tech", "quantity": 1},
                    {"required_id": "thermal_regulation_network", "required_type": "uber_tech", "quantity": 1},
                    {"required_id": "stellar_manipulation_array", "required_type": "uber_tech", "quantity": 1}
                ]
            },
            
            "civilization_capabilities": {
                # Define which tech groups each civilization can develop
                "Thrizoth": ["A", "B", "C", "D", "E"],
                "Methane Collective": ["A", "B", "C", "D", "F"],
                "Silicon Liberation": ["A", "B", "C", "D"],
                "Glacian Current": ["A", "B", "C", "E"],
                "Kyrathi": ["A", "B", "C", "E"],
                "Vasku": ["A", "B", "C", "F"]
            },
            
            "project_effects": {
                # Effects of Universal Projects
                "dyson_sphere": {
                    "beneficiaries": ["Silicon Liberation", "Vasku"],
                    "harmed": ["Thrizoth", "Glacian Current"],
                    "point_bonus": 1,  # Points per turn for beneficiaries
                    "point_penalty": -1  # Points per turn for harmed
                },
                "galactic_wormhole_network": {
                    "beneficiaries": ["Vasku", "Methane Collective"],
                    "harmed": ["Glacian Current", "Kyrathi"],
                    "point_bonus": 1,
                    "point_penalty": -1
                },
                "quantum_consciousness_grid": {
                    "beneficiaries": ["Silicon Liberation", "Kyrathi"],
                    "harmed": ["Thrizoth", "Methane Collective"],
                    "point_bonus": 1,
                    "point_penalty": -1
                }
            }
        }
    
    def validate(self) -> bool:
        """Validate the configuration."""
        # Validate components exist
        if not self.components:
            print("Validation failed: No components defined")
            return False
        
        # Validate requirements reference valid components
        for component_id, requirements in self.requirements.items():
            if component_id not in self.components:
                print(f"Validation failed: Requirements found for unknown component {component_id}")
                return False
            
            for requirement in requirements:
                # Validate big_tech and uber_tech references
                if requirement.required_type in ["big_tech", "uber_tech"]:
                    if requirement.required_id not in self.components:
                        print(f"Validation failed: Requirement references unknown component {requirement.required_id}")
                        return False
                    
                    # Verify the correct type
                    component = self.components[requirement.required_id]
                    if component.tech_type != requirement.required_type:
                        print(f"Validation failed: Component {requirement.required_id} has type {component.tech_type} but requirement expects {requirement.required_type}")
                        return False
        
        # Validate project effects reference valid projects
        for project_id in self.project_effects:
            if project_id not in self.components:
                print(f"Validation failed: Effect references unknown project {project_id}")
                return False
            
            # Verify it's a universal project
            if self.components[project_id].tech_type != "universal_project":
                print(f"Validation failed: Project effect for {project_id} is not a universal_project")
                return False
        
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
            "civilization_capabilities": self.civilization_capabilities,
            "project_effects": self.project_effects
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TechnologyConfig':
        """Create configuration from dictionary."""
        config = super(TechnologyConfig, cls).from_dict(data)
        
        # Clear defaults
        config.components = {}
        config.requirements = {}
        config.civilization_capabilities = {}
        config.project_effects = {}
        
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
        
        # Load project effects
        config.project_effects = data.get("project_effects", {})
        
        return config
    
    def can_civilization_develop(self, civilization_id: str, component_id: str) -> bool:
        """Check if a civilization can develop a specific technology component."""
        if component_id not in self.components:
            return False
            
        component = self.components[component_id]
        
        # Check if civilization is in restriction list
        if civilization_id in component.civilization_restrictions:
            return False
            
        # For big_tech, check tech group
        if component.tech_type == "big_tech" and component.tech_group:
            allowed_groups = self.civilization_capabilities.get(civilization_id, [])
            return component.tech_group in allowed_groups
            
        # For universal_project, check if civilization is harmed by it
        if component.tech_type == "universal_project":
            project_effect = self.project_effects.get(component_id, {})
            if civilization_id in project_effect.get("harmed", []):
                return False
            
        return True
    
    def get_development_requirements(self, component_id: str) -> List[TechRequirement]:
        """Get all requirements for developing a technology component."""
        return self.requirements.get(component_id, [])
    
    def get_technology_tree(self, tech_type: Optional[str] = None, max_depth: int = 3) -> Dict[str, Any]:
        """
        Build a technology dependency tree for visualization or analysis.
        
        Args:
            tech_type: Optional filter for technology type
            max_depth: Maximum depth of dependency tree to prevent infinite recursion
            
        Returns:
            Dictionary representing the technology tree
        """
        # Filter components by type if requested
        components_to_process = {
            cid: comp for cid, comp in self.components.items() 
            if not tech_type or comp.tech_type == tech_type
        }
        
        result = {}
        
        def build_tree(component_id: str, current_depth: int = 0) -> Dict[str, Any]:
            if current_depth >= max_depth:
                return {"max_depth_reached": True}
                
            component = self.components.get(component_id)
            if not component:
                return None
                
            reqs = self.requirements.get(component_id, [])
            dependencies = {}
            
            for req in reqs:
                if req.required_type in ["big_tech", "uber_tech"]:
                    dependencies[req.required_id] = build_tree(
                        req.required_id, current_depth + 1
                    )
                else:
                    # For resources, just add basic info
                    dependencies[req.required_id] = {
                        "type": req.required_type,
                        "quantity": req.quantity
                    }
                    
            return {
                "name": component.name,
                "type": component.tech_type,
                "group": component.tech_group,
                "dependencies": dependencies
            }
        
        # Build tree for each top-level component
        for component_id, component in components_to_process.items():
            if component.tech_type == "universal_project":
                result[component_id] = build_tree(component_id)
        
        return result
    
    def get_technologies_for_civilization(self, civilization_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all technologies that a civilization can develop, organized by type.
        
        Args:
            civilization_id: The ID of the civilization
            
        Returns:
            Dictionary mapping tech_type to list of available technologies
        """
        result = {"big_tech": [], "uber_tech": [], "universal_project": []}
        
        for component_id, component in self.components.items():
            if self.can_civilization_develop(civilization_id, component_id):
                result[component.tech_type].append({
                    "id": component_id,
                    "name": component.name,
                    "description": component.description,
                    "tech_group": component.tech_group
                })
                
        return result
    
    def get_project_effect(self, project_id: str, civilization_id: str) -> Dict[str, Any]:
        """
        Get the effect of a universal project on a specific civilization.
        
        Args:
            project_id: The ID of the universal project
            civilization_id: The ID of the civilization
            
        Returns:
            Dictionary with effect details
        """
        if project_id not in self.project_effects:
            return {"effect": "none", "points": 0}
            
        effects = self.project_effects[project_id]
        
        if civilization_id in effects.get("beneficiaries", []):
            return {
                "effect": "beneficial", 
                "points": effects.get("point_bonus", 1)
            }
        elif civilization_id in effects.get("harmed", []):
            return {
                "effect": "harmful", 
                "points": effects.get("point_penalty", -1)
            }
        else:
            return {"effect": "neutral", "points": 0}