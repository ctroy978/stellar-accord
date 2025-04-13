# File Path: backend/app/core/config_loader.py
# Purpose: Contains functions to load, parse, and pre-process YAML configuration files.

import yaml
import os
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

# Define a type alias for loaded YAML data for clarity
ConfigData = Dict[str, Any]

def _load_yaml_file(file_path: Path) -> Optional[ConfigData]:
    """
    Safely loads a single YAML file.

    Args:
        file_path: The Path object pointing to the YAML file.

    Returns:
        A dictionary containing the parsed YAML data, or None if loading fails.
    """
    if not file_path.is_file():
        logger.error(f"Configuration file not found: {file_path}")
        return None
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            if data is None: # Handle empty files
                 logger.warning(f"Configuration file is empty: {file_path}")
                 return {}
            logger.info(f"Successfully loaded configuration from: {file_path}")
            return data
    except yaml.YAMLError as e:
        logger.exception(f"Error parsing YAML file {file_path}: {e}") # Log full traceback
        return None
    except IOError as e:
        logger.exception(f"Error reading file {file_path}: {e}")
        return None
    except Exception as e:
        logger.exception(f"An unexpected error occurred loading {file_path}: {e}")
        return None

def _index_list_by_id(data: Optional[ConfigData], list_key: str, id_key: str = 'id') -> Dict[str, Any]:
    """Helper function to convert a list of dictionaries into a dict indexed by an ID."""
    indexed_dict = {}
    if data and isinstance(data.get(list_key), list):
        for item in data[list_key]:
            if isinstance(item, dict) and id_key in item:
                item_id = item[id_key]
                if item_id in indexed_dict:
                     logger.warning(f"Duplicate ID '{item_id}' found in list '{list_key}'. Overwriting.")
                indexed_dict[item_id] = item
            else:
                logger.warning(f"Item in list '{list_key}' is not a dict or missing key '{id_key}': {item}")
    return indexed_dict


def load_all_configs(config_root_dir: Path) -> Dict[str, Any]:
    """
    Loads all known configuration files from the specified root directory.

    Args:
        config_root_dir: Path object to the root configuration directory.

    Returns:
        A dictionary containing all loaded configuration data, potentially pre-processed.

    Raises:
        FileNotFoundError: If a critical configuration file is missing.
        ValueError: If a critical configuration file fails to parse.
    """
    if not config_root_dir.is_dir():
        logger.critical(f"Configuration root directory not found: {config_root_dir}")
        raise FileNotFoundError(f"Configuration root directory not found: {config_root_dir}")

    loaded_configs = {}
    critical_files = [
        "game_settings.yaml", "sector_map.yaml", "resources.yaml",
        "initial_state.yaml", "black_market.yaml", "conclave.yaml",
        "technology/big_tech.yaml", "technology/uber_tech.yaml",
        "technology/universal_projects.yaml", "technology/joiners.yaml",
        "technology/initial_blueprints.yaml", "intelligence/operations.yaml",
        "intelligence/mechanics.yaml"
    ]
    config_mapping = { # Maps file path relative to root to key in loaded_configs
        "game_settings.yaml": "game_settings",
        "sector_map.yaml": "sector_map",
        "resources.yaml": "resources_raw", # Keep raw list temporarily
        "initial_state.yaml": "initial_state",
        "black_market.yaml": "black_market",
        "conclave.yaml": "conclave",
        "technology/big_tech.yaml": "big_tech_raw",
        "technology/uber_tech.yaml": "uber_tech_raw",
        "technology/universal_projects.yaml": "universal_projects_raw",
        "technology/joiners.yaml": "joiners_raw",
        "technology/initial_blueprints.yaml": "initial_blueprints",
        "intelligence/operations.yaml": "intelligence_operations",
        "intelligence/mechanics.yaml": "intelligence_mechanics",
    }

    # Load critical files
    for file_rel_path, config_key in config_mapping.items():
        file_path = config_root_dir / file_rel_path
        data = _load_yaml_file(file_path)
        if data is None:
            # If a critical file fails loading, raise an error to prevent startup
            raise ValueError(f"Failed to load critical configuration file: {file_path}")
        loaded_configs[config_key] = data

    # Load civilizations
    loaded_configs["civilizations"] = {}
    civ_config_dir = config_root_dir / "civilizations"
    if civ_config_dir.is_dir():
        for civ_file in civ_config_dir.glob("*.yaml"):
            civ_data_raw = _load_yaml_file(civ_file)
            if civ_data_raw and isinstance(civ_data_raw.get('civilization'), dict):
                civ_data = civ_data_raw['civilization']
                civ_id = civ_data.get('id')
                if civ_id:
                    if civ_id in loaded_configs["civilizations"]:
                         logger.warning(f"Duplicate civilization ID '{civ_id}' loaded from {civ_file}. Overwriting.")
                    loaded_configs["civilizations"][civ_id] = civ_data
                else:
                    logger.warning(f"Could not find civilization ID ('id') in {civ_file}")
            else:
                logger.warning(f"Failed to load or parse civilization data correctly from {civ_file}")
    else:
        # Treat missing civilization directory as critical? Or allow running without? Assuming critical for now.
        logger.critical(f"Civilizations config directory not found or not a directory: {civ_config_dir}")
        raise FileNotFoundError(f"Civilizations config directory not found: {civ_config_dir}")

    # Post-processing and Indexing (Example)
    try:
        loaded_configs["resources_by_id"] = _index_list_by_id(loaded_configs.get("resources_raw"), "resources", "id")
        loaded_configs["big_tech_by_id"] = _index_list_by_id(loaded_configs.get("big_tech_raw"), "big_tech", "id")
        loaded_configs["uber_tech_by_id"] = _index_list_by_id(loaded_configs.get("uber_tech_raw"), "uber_tech", "id")
        loaded_configs["universal_projects_by_id"] = _index_list_by_id(loaded_configs.get("universal_projects_raw"), "universal_projects", "id")
        loaded_configs["joiners_by_id"] = _index_list_by_id(loaded_configs.get("joiners_raw"), "universal_joiners", "id") # Note list key from yaml

        # Optionally remove raw lists after indexing if not needed directly
        # del loaded_configs["resources_raw"]
        # del loaded_configs["big_tech_raw"]
        # ... etc ...
    except Exception as e:
        logger.exception("Error during config post-processing/indexing.")
        # Depending on severity, you might want to raise an error here too
        raise ValueError("Failed during configuration post-processing.") from e

    logger.info("All game configurations loaded and processed.")
    return loaded_configs