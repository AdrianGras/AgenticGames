import asyncio
from typing import AsyncGenerator

from app_layer.building.session_config import SessionConfig
from app_layer.core.runner_types import GameEvent
from app_layer.building.session_builder import AgentSessionBuilder, HumanSessionBuilder
from app_layer.io.input_source import InputSource
from typing import Optional

class DirectExecutionManager:
    """
    Manages the sequential execution of a Game Runner session.
    
    This manager provides a direct asynchronous stream of game events, 
    acting as a mediator between the runner's lifecycle and the 
    presentation layer.
    """

    def __init__(self, config: SessionConfig, input_adapter: Optional[InputSource] = None):
        """
        Initializes the manager with session parameters and the input implementation.

        Args:
            config: Configuration data defining game and participant parameters.
            input_adapter: The implementation of the InputSource to be used by the runner.
        """
        self.config = config
        self.input_adapter = input_adapter
        self.runner = self._initialize_runner()

    def _initialize_runner(self):
        """
        Constructs the GameRunner instance by injecting the required configuration 
        and the input adapter.

        Returns:
            The initialized GameRunner instance.
        """
        if self.config.is_human:
            return HumanSessionBuilder(
                game_name=self.config.game_name,
                input_adapter=self.input_adapter,
                game_params=self.config.game_params
            ).build()
        
        return AgentSessionBuilder(
            game_name=self.config.game_name,
            agent_name=self.config.agent_name,
            agent_params=self.config.agent_params,
            game_params=self.config.game_params,
        ).build()

    async def execute(self) -> AsyncGenerator[GameEvent, None]:
        """
        Iterates over the runner generator and yields events to the consumer.

        Yields:
            GameEvent: Events emitted during the game lifecycle (Start, Turn, Result).
        """
        async for event in self.runner.run():
            yield event