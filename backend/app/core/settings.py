# File Path: backend/app/core/settings.py
# Purpose: Provides a centralized access point for loaded configuration data.
# Loads configuration once at startup.

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Import the loader function
from .config_loader import load_all_configs

logger = logging.getLogger(__name__)

class Settings:
    """Holds all loaded game configuration."""

    # --- Configuration Path ---
    # Determined by environment variable CONFIG_PATH, defaults to /app/config inside the container.
    # Ensure this default matches your docker-compose.yaml volume mount target.
    CONFIG_PATH: Path = Path(os.getenv("CONFIG_PATH", "/app/config"))

    # Attributes to hold loaded config data
    game_settings: Dict[str, Any] = {}
    sector_map: Dict[str, Any] = {}
    resources_raw: Dict[str, Any] = {} # Example if keeping raw
    resources_by_id: Dict[str, Any] = {}
    initial_state: Dict[str, Any] = {}
    black_market: Dict[str, Any] = {}
    conclave: Dict[str, Any] = {}
    civilizations: Dict[str, Any] = {} # Indexed by Civ ID
    big_tech_raw: Dict[str, Any] = {} # Example if keeping raw
    big_tech_by_id: Dict[str, Any] = {}
    uber_tech_raw: Dict[str, Any] = {} # Example if keeping raw
    uber_tech_by_id: Dict[str, Any] = {}
    universal_projects_raw: Dict[str, Any] = {} # Example if keeping raw
    universal_projects_by_id: Dict[str, Any] = {}
    joiners_raw: Dict[str, Any] = {} # Example if keeping raw
    joiners_by_id: Dict[str, Any] = {}
    initial_blueprints: Dict[str, Any] = {}
    intelligence_operations: Dict[str, Any] = {}
    intelligence_mechanics: Dict[str, Any] = {}

    _loaded: bool = False # Flag to ensure loading happens only once

    def __init__(self):
        if not Settings._loaded:
            logger.info(f"Initializing configuration settings from path: {self.CONFIG_PATH}")
            try:
                loaded_data = load_all_configs(self.CONFIG_PATH)

                # Assign loaded data to class attributes
                self.game_settings = loaded_data.get("game_settings", {})
                self.sector_map = loaded_data.get("sector_map", {})
                self.resources_raw = loaded_data.get("resources_raw", {}) # Keep or remove based on need
                self.resources_by_id = loaded_data.get("resources_by_id", {})
                self.initial_state = loaded_data.get("initial_state", {})
                self.black_market = loaded_data.get("black_market", {})
                self.conclave = loaded_data.get("conclave", {})
                self.civilizations = loaded_data.get("civilizations", {})
                self.big_tech_raw = loaded_data.get("big_tech_raw", {}) # Keep or remove based on need
                self.big_tech_by_id = loaded_data.get("big_tech_by_id", {})
                self.uber_tech_raw = loaded_data.get("uber_tech_raw", {}) # Keep or remove based on need
                self.uber_tech_by_id = loaded_data.get("uber_tech_by_id", {})
                self.universal_projects_raw = loaded_data.get("universal_projects_raw", {}) # Keep or remove based on need
                self.universal_projects_by_id = loaded_data.get("universal_projects_by_id", {})
                self.joiners_raw = loaded_data.get("joiners_raw", {}) # Keep or remove based on need
                self.joiners_by_id = loaded_data.get("joiners_by_id", {})
                self.initial_blueprints = loaded_data.get("initial_blueprints", {})
                self.intelligence_operations = loaded_data.get("intelligence_operations", {})
                self.intelligence_mechanics = loaded_data.get("intelligence_mechanics", {})

                Settings._loaded = True
                logger.info("Configuration settings initialized successfully.")

            except (FileNotFoundError, ValueError, RuntimeError) as e:
                # Log critical error and potentially exit or prevent app start
                logger.critical(f"CRITICAL: Failed to initialize settings due to configuration loading error: {e}")
                # Depending on your framework setup, you might re-raise to halt startup
                raise RuntimeError("Application configuration failed to load.") from e
        else:
             logger.debug("Settings already initialized.")

    # --- Accessor Methods (optional but recommended) ---
    # Provide convenient and safe ways to access specific config parts

    def get_resource(self, resource_id: str) -> Optional[Dict[str, Any]]:
        return self.resources_by_id.get(resource_id)

    def get_big_tech(self, tech_id: str) -> Optional[Dict[str, Any]]:
        return self.big_tech_by_id.get(tech_id)

    def get_civilization(self, civ_id: str) -> Optional[Dict[str, Any]]:
        return self.civilizations.get(civ_id)

    # Add more accessors as needed...


# Create a single, global instance of the Settings class
# Other modules will import this instance to access configuration
settings = Settings()

# Example of how to use it elsewhere:
# from app.core.settings import settings
# max_rounds = settings.game_settings.get("game", {}).get("recommended_rounds", 7)
# carbon_def = settings.get_resource("CarbonMatrices")