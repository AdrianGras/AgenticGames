from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Callable, Awaitable

# Core Imports
from app_layer.game_runner import GameRunner
from game_layer.game_engine.core_engine import CoreEngine
from agent_layer.actor import Actor
from agent_layer.human_actor import HumanActor, InputSource

# Factories
from game_layer.games.game_selector import get_game
from agent_layer.agent_selector import get_agent

class SessionBuilder(ABC):
    """
    Abstract Base Class for configuring and building Game Sessions.
    """

    def __init__(self, game_name: str, game_params: Optional[Dict[str, Any]] = None):
        """
        Base initialization for shared session parameters.

        Args:
            game_name (str): Identifier of the game to load.
            game_params (dict, optional): Specific parameters for the Game constructor.
        """
        self.game_name = game_name
        self.game_params = game_params if game_params is not None else {}

    def build(self) -> GameRunner:
        """
        Executes the construction of the GameRunner using the stored configuration.

        Returns:
            GameRunner: An assembled runner ready for execution.
        
        Raises:
            ValueError: If initialization of the Game or Actor fails.
        """
        try:
            game: CoreEngine = get_game(self.game_name, **self.game_params)
        except ValueError as e:
            raise ValueError(f"SessionBuilder: Failed to initialize game '{self.game_name}'. {e}")

        actor = self._create_actor()

        return GameRunner(game, actor)

    @abstractmethod
    def _create_actor(self) -> Actor:
        """
        Internal factory method to create the specific Actor instance.
        """
        ...

class HumanSessionBuilder(SessionBuilder):
    """
    Builder strategy for Human-driven sessions.
    """

    def __init__(
        self, 
        game_name: str, 
        input_adapter: InputSource, 
        game_params: Optional[Dict[str, Any]] = None
    ):
        """
        Args:
            game_name (str): The game to play.
            input_adapter (InputSource): Interface for reading human input.
            game_params (dict, optional): Configuration for the game.
        """
        # Pass game config to parent
        super().__init__(game_name, game_params)
        self.input_adapter = input_adapter

    def _create_actor(self) -> Actor:
        return HumanActor(input_queue=self.input_adapter)

class AgentSessionBuilder(SessionBuilder):
    """
    Builder strategy for Agent-driven sessions.
    """

    def __init__(
        self, 
        game_name: str,
        agent_name: str, 
        game_params: Optional[Dict[str, Any]] = None,
        agent_params: Optional[Dict[str, Any]] = None
    ):
        """
        Args:
            game_name (str): The game to play.
            agent_name (str): The ID of the agent logic.
            model_name (str): The ID of the LLM model.
            on_reasoning (Callable, optional): Callback for streaming thought process.
            game_params (dict, optional): Configuration for the game.
            agent_params (dict, optional): Configuration for the agent.
        """
        # Pass game config to parent
        super().__init__(game_name, game_params)
        
        self.agent_name = agent_name
        self.agent_params = agent_params if agent_params is not None else {}

    def _create_actor(self) -> Actor:
        try:
            return get_agent(
                agent_id=self.agent_name,
                **self.agent_params
            )
        except ValueError as e:
            raise ValueError(f"AgentSessionBuilder: Failed to initialize agent. {e}")