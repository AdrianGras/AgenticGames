import asyncio
from typing import List, Optional, Union, Any

from app_layer.session_config import SessionConfig
from app_layer.runner_types import GameEvent
from app_layer.session_builder import AgentSessionBuilder, HumanSessionBuilder

# Type alias for cleaner signatures

class GameExecutionManager:
    """
    Manages the asynchronous lifecycle and state of a Game Runner session.
    
    This manager coordinates data flow between the domain logic and the UI, 
    handling input/output buffering, agent reasoning streams, and execution 
    flow control (Play/Pause/Step).
    """

    def __init__(self, config: SessionConfig):
        """
        Initializes the manager and sets the initial execution state based on player type.
        
        Args:
            config: Configuration object defining session parameters and player types.
        """
        self.config = config
        
        self._input_queue: asyncio.Queue[str] = asyncio.Queue()
        self._output_queue: asyncio.Queue[GameEvent] = asyncio.Queue()
        self._reasoning_queue: asyncio.Queue[Any] = asyncio.Queue()
        
        self._resume_event = asyncio.Event()
        self._single_step_mode = False

        if self.config.is_human:
            self._resume_event.set() 
        else:
            self._resume_event.clear()

        self.runner = self._initialize_runner()

    def _initialize_runner(self):
        """
        Builds the GameRunner instance and injects required communication adapters.
        
        Returns:
            The constructed GameRunner instance.
        """
        if self.config.is_human:
            return HumanSessionBuilder(
                game_name=self.config.game_name,
                input_adapter=self._input_queue,
                game_params=self.config.game_params
            ).build()
        else:
            self.config.agent_params["on_reasoning"] = self._on_agent_reasoning 
            return AgentSessionBuilder(
                game_name=self.config.game_name,
                agent_name=self.config.agent_name,
                agent_params=self.config.agent_params,
                game_params=self.config.game_params,
            ).build()

    async def _on_agent_reasoning(self, data: Any) -> None:
        """
        Callback handler for agent reasoning tokens.
        
        Args:
            data: The reasoning data emitted by the agent actor.
        """
        await self._reasoning_queue.put(data)

    async def start(self) -> None:
        """
        Starts the asynchronous execution loop.
        
        Iterates over the runner generator and manages the flow control barrier.
        The wait happens at the end of the loop to ensure the current step is 
        always processed before pausing.
        """
        try:
            async for step in self.runner.run():
                await self._output_queue.put(step)

                if self._single_step_mode:
                    self._resume_event.clear()
                    self._single_step_mode = False

                await self._resume_event.wait()
                
                await asyncio.sleep(0.01)

        except Exception as e:
            await self._output_queue.put(GameResult(final_status=f"ERROR: {str(e)}"))

    def play(self) -> None:
        """Opens the execution gate to run the game loop continuously."""
        self._single_step_mode = False
        self._resume_event.set()

    def pause(self) -> None:
        """Closes the execution gate to halt the game loop."""
        self._single_step_mode = False
        self._resume_event.clear()

    def step(self) -> None:
        """Executes a single iteration of the game loop and re-locks the execution gate."""
        if not self._resume_event.is_set():
            self._single_step_mode = True
            self._resume_event.set()

    def enqueue_user_input(self, text: str) -> None:
        """
        Adds user input to the runner's input queue.
        
        Args:
            text: The command or text input from the user interface.
        """
        if text:
            self._input_queue.put_nowait(text)

    async def pop_pending_updates(self) -> Optional[List[GameEvent]]:
        """
        Drains the output queue and returns the raw Domain Objects.
        The Presentation Layer is responsible for formatting them.
        
        Returns:
            A list of GameStart, GameTurn, or GameResult objects, or None if empty.
        """
        if self._output_queue.empty():
            return None
        
        updates = []
        while not self._output_queue.empty():
            updates.append(await self._output_queue.get())
        
        return updates

    async def pop_reasoning(self) -> Optional[List[Any]]:
        """
        Drains the reasoning queue and returns the accumulated tokens.
        
        Returns:
            A list of raw reasoning data chunks or None if empty.
        """
        if self._reasoning_queue.empty():
            return None
            
        tokens = []
        while not self._reasoning_queue.empty():
            tokens.append(await self._reasoning_queue.get())
        
        return tokens