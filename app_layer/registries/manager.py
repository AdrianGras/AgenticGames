import logging
from typing import Optional
from .generic_registry import GenericRegistry

# Domain type imports
from game_layer.game_engine.core_engine import CoreEngine
from agent_layer.actor import Actor

# Private registry instances
_game_registry: Optional[GenericRegistry[CoreEngine]] = None
_agent_registry: Optional[GenericRegistry[Actor]] = None

def get_game_registry() -> GenericRegistry[CoreEngine]:
    """
    Retrieves the global Game Registry. Initializes and scans the game 
    directory if the registry instance does not exist.
    """
    global _game_registry
    if _game_registry is None:
        _game_registry = GenericRegistry[CoreEngine]("GameRegistry")
        _run_discovery("game_layer/games", _game_registry)
    return _game_registry

def get_agent_registry() -> GenericRegistry[Actor]:
    """
    Retrieves the global Agent Registry. Initializes and scans the agent 
    directory if the registry instance does not exist.
    """
    global _agent_registry
    if _agent_registry is None:
        _agent_registry = GenericRegistry[Actor]("AgentRegistry")
        _run_discovery("agent_layer/llm_agents", _agent_registry)
    return _agent_registry

def _run_discovery(path: str, registry: GenericRegistry) -> None:
    """
    Internal helper to trigger the discovery mechanism for a targeted path.
    """
    try:
        from .discovery import discover_entities
        discover_entities(path, registry)
    except Exception as e:
        logging.error(f"Discovery failed for path '{path}': {e}")
        raise