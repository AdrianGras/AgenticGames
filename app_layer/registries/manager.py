import logging
from typing import Optional
from .generic_registry import GenericRegistry

# Domain type imports for type hinting
from game_layer.game_engine.core_engine import CoreEngine
from agent_layer.actor import Actor

# Private registry instances (Singleton Pattern)
_game_registry: Optional[GenericRegistry[CoreEngine]] = None
_agent_registry: Optional[GenericRegistry[Actor]] = None

def get_game_registry() -> GenericRegistry[CoreEngine]:
    """
    Retrieves the global Game Registry instance.

    If the registry has not been initialized, this function triggers the 
    automatic discovery process to scan the 'game_layer' for manifests.

    Returns:
        GenericRegistry[CoreEngine]: The central registry for all discovered games.
    """
    global _game_registry
    if _game_registry is None:
        _game_registry = GenericRegistry[CoreEngine]("GameRegistry")
        _run_discovery()
    return _game_registry

def get_agent_registry() -> GenericRegistry[Actor]:
    """
    Retrieves the global Agent Registry instance.

    If the registry has not been initialized, this function triggers the 
    automatic discovery process to scan the 'agent_layer' for manifests.

    Returns:
        GenericRegistry[Actor]: The central registry for all discovered agents.
    """
    global _agent_registry
    if _agent_registry is None:
        _agent_registry = GenericRegistry[Actor]("AgentRegistry")
        _run_discovery()
    return _agent_registry

def _run_discovery() -> None:
    """
    Internal helper to execute the discovery mechanism.
    
    This is called lazily during the first registry access to populate 
    entities from the file system into the registry instances.
    """
    try:
        from .discovery import discover_entities
        discover_entities()
    except Exception as e:
        logging.error(f"Failed to discover registry entities: {e}")
        raise