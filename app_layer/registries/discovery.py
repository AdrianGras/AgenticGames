import importlib
import inspect
import logging
from pathlib import Path
from .generic_registry import EntityManifest, GenericRegistry

logger = logging.getLogger(__name__)

def discover_entities(search_path_str: str, registry: GenericRegistry) -> None:
    """
    Scans a specific directory for 'manifest.py' files and registers 
    discovered EntityManifest instances into the provided registry.

    Args:
        search_path_str: Relative path from project root (e.g., 'game_layer/games').
        registry: The specific registry instance to populate.
    """
    project_root = Path.cwd()
    search_path = project_root / search_path_str
    
    if not search_path.exists():
        logger.warning(f"Search path does not exist: {search_path}")
        return

    for manifest_file in search_path.rglob("manifest.py"):
        try:
            # Convert filesystem path to python module dotted path
            relative_path = manifest_file.relative_to(project_root)
            module_path = ".".join(relative_path.with_suffix("").parts)
            
            _process_manifest_module(module_path, registry)
            
        except Exception as e:
            logger.error(f"Failed to resolve module path for {manifest_file}: {e}")

def _process_manifest_module(module_path: str, registry: GenericRegistry) -> None:
    """
    Imports a manifest module and inspects its members for EntityManifest instances.
    """
    try:
        module = importlib.import_module(module_path)
        
        for _, obj in inspect.getmembers(module):
            if isinstance(obj, EntityManifest):
                # Safety check to prevent ID collisions within the same registry
                if obj.id in registry.list_ids():
                    logger.debug(f"Entity '{obj.id}' already in {registry.name}. Skipping.")
                    continue
                    
                registry.register(obj)
                logger.debug(f"Successfully registered '{obj.id}' from {module_path}")
            
    except ImportError as e:
        logger.error(f"Could not import module {module_path}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error processing {module_path}: {e}")