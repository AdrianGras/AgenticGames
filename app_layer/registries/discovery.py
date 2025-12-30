import importlib
import inspect
import pkgutil
import logging
from pathlib import Path
from .generic_registry import EntityManifest, GenericRegistry

# Setup logging configuration
logger = logging.getLogger(__name__)

def discover_entities() -> None:
    """
    Dynamically scans the project structure for 'manifest.py' modules and 
    registers discovered EntityManifest instances into their respective registries.

    This function performs the following steps:
    1. Defines search paths for games and agents.
    2. Recursively crawls packages using pkgutil.
    3. Imports any module named 'manifest'.
    4. Inspects module members to find instances of EntityManifest.
    5. Dispatches manifests to the appropriate Registry (Game or Agent).
    """
    # Local imports to prevent circular dependencies with manager.py
    from .manager import get_game_registry, get_agent_registry
    
    game_reg = get_game_registry()
    agent_reg = get_agent_registry()

    # Define base packages to scan
    search_targets = [
        {"pkg_name": "game_layer.games", "registry": game_reg},
        {"pkg_name": "agent_layer.llm_agents", "registry": agent_reg}
    ]

    for target in search_targets:
        try:
            root_module = importlib.import_module(target["pkg_name"])
            root_path = root_module.__path__
            
            # Recursive scan of the package hierarchy
            for loader, mod_name, is_pkg in pkgutil.walk_packages(root_path, target["pkg_name"] + "."):
                if mod_name.endswith(".manifest"):
                    _process_manifest_module(mod_name, target["registry"])
                    
        except ImportError as e:
            logger.warning(f"Could not import root package {target['pkg_name']}: {e}")

def _process_manifest_module(module_path: str, registry: GenericRegistry) -> None:
    """
    Imports a specific manifest module and inspects its members for EntityManifest instances.

    Args:
        module_path: The full python path to the module (e.g., 'game_layer.games.logic.manifest').
        registry: The Registry instance where the discovered manifest will be stored.
    """
    try:
        module = importlib.import_module(module_path)
        
        # Iterate over all members of the imported module
        found_any = False
        for name, obj in inspect.getmembers(module):
            # Check if the object is an instance of EntityManifest
            if isinstance(obj, EntityManifest):
                registry.register(obj)
                found_any = True
                logger.debug(f"Registered entity '{obj.id}' from {module_path}")
        
        if not found_any:
            logger.warning(f"Module {module_path} was imported but no EntityManifest instance was found.")
            
    except Exception as e:
        logger.error(f"Error processing manifest at {module_path}: {e}")