from dataclasses import dataclass, field
from typing import Dict, Any, Optional

@dataclass
class SessionConfig:
    """
    Structured configuration object for initializing a Game Session.
    """
    game_name: str
    is_human: bool
    agent_name: Optional[str] = None
    game_params: Dict[str, Any] = field(default_factory=dict)
    agent_params: Optional[Dict[str, Any]] = None