# app/config/law_system.py
from typing import Dict, List, Any, Optional, Union
from uuid import UUID
from app.config.base import BaseConfiguration

class LawTemplate:
    """Represents a law template that can be used to create laws."""
    
    def __init__(self, template_id: str, name: str, description: str,
                 template_text: str, parameters: List[Dict[str, Any]],
                 effects: Optional[Dict[str, Any]] = None,
                 category: Optional[str] = None):
        self.template_id = template_id
        self.name = name
        self.description = description
        self.template_text = template_text  # Text with placeholders like [PARAMETER]
        self.parameters = parameters  # List of parameter definitions
        self.effects = effects or {}  # Game effects when law is active
        self.category = category  # Optional category for grouping
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "template_id": self.template_id,
            "name": self.name,
            "description": self.description,
            "template_text": self.template_text,
            "parameters": self.parameters,
            "effects": self.effects,
            "category": self.category
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LawTemplate':
        """Create from dictionary."""
        return cls(
            template_id=data["template_id"],
            name=data["name"],
            description=data.get("description", ""),
            template_text=data["template_text"],
            parameters=data.get("parameters", []),
            effects=data.get("effects", {}),
            category=data.get("category")
        )

class LawSystemConfig(BaseConfiguration):
    """Configuration for the law system, including templates and mechanics."""
    
    def __init__(self, config_id: Optional[UUID] = None):
        super().__init__(config_id)
        self.law_templates = {}  # template_id -> LawTemplate
        self.max_laws_per_category = {}  # category -> max count
        self.voting_rules = {}  # Rules for voting on laws
        self._load_defaults()
    
    def _load_defaults(self):
        """Load default law system configuration."""
        defaults = self.get_defaults()
        
        # Load law templates
        for template_data in defaults.get("law_templates", []):
            template = LawTemplate.from_dict(template_data)
            self.law_templates[template.template_id] = template
        
        # Load other settings
        self.max_laws_per_category = defaults.get("max_laws_per_category", {})
        self.voting_rules = defaults.get("voting_rules", {})
    
    def get_defaults(self) -> Dict[str, Any]:
        """Return default configuration values."""
        return {
            "law_templates": [
                # Resource Tax Law
                {
                    "template_id": "resource_tax_law",
                    "name": "Resource Tax Law",
                    "description": "Sets a tax on trading specific resources",
                    "template_text": "Trading of [RESOURCE_TYPE] requires a tax payment of [TAX_PERCENTAGE]% to the Kokoro Conclave treasury.",
                    "parameters": [
                        {
                            "name": "RESOURCE_TYPE",
                            "type": "resource_category",
                            "description": "Type or category of resource to tax"
                        },
                        {
                            "name": "TAX_PERCENTAGE",
                            "type": "range",
                            "min": 5,
                            "max": 30,
                            "description": "Percentage of resource value to be paid as tax"
                        }
                    ],
                    "effects": {
                        "type": "resource_tax",
                        "applies_to": "trade"
                    },
                    "category": "economic"
                },
                
                # Resource Quota System
                {
                    "template_id": "resource_quota_system",
                    "name": "Resource Quota System",
                    "description": "Requires civilizations to contribute resources to an initiative",
                    "template_text": "All civilizations must contribute [QUOTA_AMOUNT] units of [RESOURCE_TYPE] per round to the [PROGRAM_NAME] initiative.",
                    "parameters": [
                        {
                            "name": "QUOTA_AMOUNT",
                            "type": "range",
                            "min": 5,
                            "max": 25,
                            "description": "Amount of resource required per round"
                        },
                        {
                            "name": "RESOURCE_TYPE",
                            "type": "resource_type",
                            "description": "Specific resource required"
                        },
                        {
                            "name": "PROGRAM_NAME",
                            "type": "text",
                            "description": "Name of the initiative"
                        }
                    ],
                    "effects": {
                        "type": "resource_quota",
                        "applies_to": "all_civilizations"
                    },
                    "category": "economic"
                },
                
                # Project Development Ban
                {
                    "template_id": "project_development_ban",
                    "name": "Project Development Ban",
                    "description": "Prohibits development of specific projects without a license",
                    "template_text": "Development of [PROJECT_NAME] is prohibited without a special license costing [LICENSE_COST] units of [RESOURCE_TYPE].",
                    "parameters": [
                        {
                            "name": "PROJECT_NAME",
                            "type": "project",
                            "description": "Project to restrict"
                        },
                        {
                            "name": "LICENSE_COST",
                            "type": "range",
                            "min": 100,
                            "max": 300,
                            "description": "Cost of development license"
                        },
                        {
                            "name": "RESOURCE_TYPE",
                            "type": "resource_type",
                            "description": "Resource for license payment"
                        }
                    ],
                    "effects": {
                        "type": "project_restriction",
                        "applies_to": "specific_project"
                    },
                    "category": "technology"
                },
                
                # Uber-Tech Component Licensing
                {
                    "template_id": "uber_tech_licensing",
                    "name": "Uber-Tech Component Licensing",
                    "description": "Requires licenses for producing Uber-Tech components",
                    "template_text": "Production of [UBER_TECH_COMPONENT] requires a license costing [LICENSE_COST] units of [RESOURCE_TYPE] paid to the Conclave treasury.",
                    "parameters": [
                        {
                            "name": "UBER_TECH_COMPONENT",
                            "type": "uber_tech",
                            "description": "Uber-Tech component requiring licensing"
                        },
                        {
                            "name": "LICENSE_COST",
                            "type": "range",
                            "min": 50,
                            "max": 200,
                            "description": "Cost of production license"
                        },
                        {
                            "name": "RESOURCE_TYPE",
                            "type": "resource_type",
                            "description": "Resource for license payment"
                        }
                    ],
                    "effects": {
                        "type": "component_licensing",
                        "applies_to": "uber_tech"
                    },
                    "category": "technology"
                },
                
                # Chrono Shard Regulation
                {
                    "template_id": "chrono_shard_regulation",
                    "name": "Chrono Shard Regulation",
                    "description": "Regulates large Chrono Shard transactions",
                    "template_text": "All Chrono Shard transactions exceeding [THRESHOLD] CS must be registered with the Conclave and incur a [FEE_PERCENTAGE]% transaction fee.",
                    "parameters": [
                        {
                            "name": "THRESHOLD",
                            "type": "number",
                            "description": "Threshold for transaction regulation"
                        },
                        {
                            "name": "FEE_PERCENTAGE",
                            "type": "range",
                            "min": 5,
                            "max": 20,
                            "description": "Transaction fee percentage"
                        }
                    ],
                    "effects": {
                        "type": "chrono_shard_fee",
                        "applies_to": "black_market"
                    },
                    "category": "economic"
                },
                
                # Trade Route Taxation
                {
                    "template_id": "trade_route_taxation",
                    "name": "Trade Route Taxation",
                    "description": "Sets tax on trades through specific regions",
                    "template_text": "Trade passing through [REGION] incurs a [TAX_PERCENTAGE]% tariff payable to the Kokoro Conclave treasury.",
                    "parameters": [
                        {
                            "name": "REGION",
                            "type": "star_system",
                            "description": "Region where tariff applies"
                        },
                        {
                            "name": "TAX_PERCENTAGE",
                            "type": "range",
                            "min": 5,
                            "max": 25,
                            "description": "Tariff percentage"
                        }
                    ],
                    "effects": {
                        "type": "route_tax",
                        "applies_to": "trade"
                    },
                    "category": "economic"
                },
                
                # Black Market Crackdown
                {
                    "template_id": "black_market_crackdown",
                    "name": "Black Market Crackdown",
                    "description": "Increases enforcement against black market operations",
                    "template_text": "The Conclave authorizes enforcement against black market operations in [REGION] for the next [DURATION] rounds. Violators forfeit [PENALTY] units of [RESOURCE_TYPE].",
                    "parameters": [
                        {
                            "name": "REGION",
                            "type": "star_system",
                            "description": "Region of crackdown"
                        },
                        {
                            "name": "DURATION",
                            "type": "range",
                            "min": 1,
                            "max": 3,
                            "description": "Duration of crackdown in rounds"
                        },
                        {
                            "name": "PENALTY",
                            "type": "range",
                            "min": 50,
                            "max": 200,
                            "description": "Penalty amount"
                        },
                        {
                            "name": "RESOURCE_TYPE",
                            "type": "resource_type",
                            "description": "Resource type for penalties"
                        }
                    ],
                    "effects": {
                        "type": "black_market_penalty",
                        "applies_to": "specific_region"
                    },
                    "category": "security"
                },
                
                # Universal Project Taxation
                {
                    "template_id": "project_taxation",
                    "name": "Universal Project Taxation",
                    "description": "Taxes the completion of Universal Projects",
                    "template_text": "Upon completion of any Universal Project, the builder must pay [TAX_PERCENTAGE]% of construction resources to the Kokoro Conclave treasury.",
                    "parameters": [
                        {
                            "name": "TAX_PERCENTAGE",
                            "type": "range",
                            "min": 10,
                            "max": 30,
                            "description": "Tax percentage on resources"
                        }
                    ],
                    "effects": {
                        "type": "project_tax",
                        "applies_to": "universal_projects"
                    },
                    "category": "technology"
                },
                
                # Project Benefit Distribution
                {
                    "template_id": "benefit_distribution",
                    "name": "Project Benefit Distribution",
                    "description": "Forces sharing of project benefits",
                    "template_text": "Benefits from [PROJECT_NAME] must be shared with [BENEFICIARIES] for [DURATION] rounds after completion.",
                    "parameters": [
                        {
                            "name": "PROJECT_NAME",
                            "type": "project",
                            "description": "Project with shared benefits"
                        },
                        {
                            "name": "BENEFICIARIES",
                            "type": "civilization_list",
                            "description": "Civilizations receiving benefits"
                        },
                        {
                            "name": "DURATION",
                            "type": "range",
                            "min": 1,
                            "max": 5,
                            "description": "Duration of benefit sharing"
                        }
                    ],
                    "effects": {
                        "type": "benefit_sharing",
                        "applies_to": "specific_project"
                    },
                    "category": "diplomacy"
                }
            ],
            
            "max_laws_per_category": {
                "economic": 3,
                "technology": 2,
                "security": 1,
                "diplomacy": 2
            },
            
            "voting_rules": {
                "submission_counts_as_vote": True,
                "tiebreaker": "none",  # Options: "none", "random", "oldest_first"
                "abstain_allowed": False
            }
        }
    
    def validate(self) -> bool:
        """Validate the configuration."""
        # Ensure we have law templates
        if not self.law_templates:
            return False
        
        # Validate template parameters
        for template_id, template in self.law_templates.items():
            # Check template has parameters for all placeholders
            placeholders = []
            text = template.template_text
            i = 0
            while i < len(text):
                if text[i] == '[':
                    start = i
                    i += 1
                    while i < len(text) and text[i] != ']':
                        i += 1
                    if i < len(text) and text[i] == ']':
                        placeholders.append(text[start+1:i])
                i += 1
            
            parameter_names = [p["name"] for p in template.parameters]
            if not all(p in parameter_names for p in placeholders):
                return False
        
        # Check that max laws per category includes all categories
        categories = set(template.category for template in self.law_templates.values() 
                        if template.category)
        if not all(category in self.max_laws_per_category for category in categories):
            return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        data = super().to_dict()
        data.update({
            "law_templates": [template.to_dict() for template in self.law_templates.values()],
            "max_laws_per_category": self.max_laws_per_category,
            "voting_rules": self.voting_rules
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LawSystemConfig':
        """Create configuration from dictionary."""
        config = super(LawSystemConfig, cls).from_dict(data)
        
        # Clear defaults
        config.law_templates = {}
        
        # Load templates
        for template_data in data.get("law_templates", []):
            template = LawTemplate.from_dict(template_data)
            config.law_templates[template.template_id] = template
        
        # Load other settings
        config.max_laws_per_category = data.get("max_laws_per_category", {})
        config.voting_rules = data.get("voting_rules", {})
        
        return config
    
    def get_template(self, template_id: str) -> Optional[LawTemplate]:
        """Get a law template by ID."""
        return self.law_templates.get(template_id)
    
    def get_templates_by_category(self, category: Optional[str] = None) -> List[LawTemplate]:
        """Get all templates in a specific category, or all if None."""
        if category is None:
            return list(self.law_templates.values())
        
        return [t for t in self.law_templates.values() if t.category == category]
    
    def get_max_laws(self, category: str) -> int:
        """Get the maximum number of laws allowed for a category."""
        return self.max_laws_per_category.get(category, 0)
    
    def render_law_text(self, template_id: str, parameters: Dict[str, Any]) -> str:
        """
        Render the complete text of a law from template and parameters.
        
        Args:
            template_id: ID of the law template
            parameters: Dictionary mapping parameter names to values
            
        Returns:
            Complete law text with parameters filled in
        """
        template = self.get_template(template_id)
        if not template:
            return ""
        
        text = template.template_text
        
        # Replace all parameters
        for param_name, param_value in parameters.items():
            placeholder = f"[{param_name}]"
            text = text.replace(placeholder, str(param_value))
        
        return text
    
    def calculate_effects(self, template_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate the game effects of a law based on its template and parameters.
        
        Args:
            template_id: ID of the law template
            parameters: Dictionary mapping parameter names to values
            
        Returns:
            Dictionary describing the effects
        """
        template = self.get_template(template_id)
        if not template or not template.effects:
            return {}
        
        # Start with the base effects
        effects = template.effects.copy()
        
        # Add parameter values
        effects["parameters"] = parameters
        
        return effects