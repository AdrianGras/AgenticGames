import importlib
import inspect
import logging
from pathlib import Path
from .generic_registry import EntityManifest, GenericRegistry

# Setup logging configuration
logger = logging.getLogger(__name__)

def discover_entities() -> None:
    """
    Dynamically scans the project filesystem for 'manifest.py' files and 
    registers discovered EntityManifest instances into their respective registries.

    This approach uses pathlib to find files, making it more robust than pkgutil
    when __init__.py files are missing in subdirectories.
    """
    # Local imports to prevent circular dependencies
    from .manager import get_game_registry, get_agent_registry
    
    game_reg = get_game_registry()
    agent_reg = get_agent_registry()

    # Define directories to scan
    # 'path' is the folder to search, 'registry' is where to store findings
    search_targets = [
        {"path": "game_layer/games", "registry": game_reg},
        {"path": "agent_layer/llm_agents", "registry": agent_reg}
    ]

    # The project root is assumed to be the current working directory where app.py runs
    project_root = Path.cwd()

    for target in search_targets:
        search_path = project_root / target["path"]
        
        if not search_path.exists():
            logger.warning(f"Search path does not exist: {search_path}")
            continue

        # rglob("manifest.py") finds all 'manifest.py' files in any subfolder
        for manifest_file in search_path.rglob("manifest.py"):
            try:
                relative_path = manifest_file.relative_to(project_root)
                module_path = ".".join(relative_path.with_suffix("").parts)
                
                logger.info(f"Discovering manifest at: {module_path}")
                _process_manifest_module(module_path, target["registry"])
                
            except Exception as e:
                logger.error(f"Failed to resolve module path for {manifest_file}: {e}")

def _process_manifest_module(module_path: str, registry: GenericRegistry) -> None:
    """
    Imports a specific manifest module and inspects its members for EntityManifest instances.

    Args:
        module_path: The full python dotted path (e.g., 'game_layer.games.logic.manifest').
        registry: The Registry instance where the discovered manifest will be stored.
    """
    try:
        # Dynamically import the module
        module = importlib.import_module(module_path)
        
        found_any = False
        # Iterate over all members of the imported module
        for name, obj in inspect.getmembers(module):
            # Check if the object is an instance of EntityManifest
            if isinstance(obj, EntityManifest):
                registry.register(obj)
                found_any = True
                logger.debug(f"Successfully registered entity '{obj.id}' from {module_path}")
        
        if not found_any:
            logger.warning(f"Module {module_path} was imported but no EntityManifest instance was found.")
            
    except ImportError as e:
        logger.error(f"Could not import module {module_path}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error processing {module_path}: {e}")