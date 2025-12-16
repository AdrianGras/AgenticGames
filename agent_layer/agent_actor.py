import re
from abc import ABC
from typing import Any, Callable, Awaitable, Optional
from agent_layer.actor import Actor

ReasoningCallback = Callable[[Any], Awaitable[None]]

class AgentActor(Actor, ABC):
    """
    Abstract Base Class for AI-controlled actors.
    
    It extends the Actor interface by adding a mechanism to stream 
    internal reasoning (thoughts, graph updates, logs) to the UI 
    via a callback, without coupling the game logic to the reasoning format.
    """

    def __init__(self, on_reasoning: Optional[ReasoningCallback] = None):
        """
        Args:
            on_reasoning: An optional async callback to handle real-time 
                          reasoning updates (e.g., streaming text tokens, 
                          updates to a knowledge graph, or debug info).
        """
        self.on_reasoning = on_reasoning

    async def emit_reasoning(self, data: Any) -> None:
        """
        Helper method to send reasoning data to the observer (UI).
        Subclasses should call this during their get_action execution.
        """
        if self.on_reasoning:
            await self.on_reasoning(data)
