from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import List, Any, Optional

class GameStatus(Enum):
    RUNNING = auto()
    FINISHED = auto()
    FAILED = auto()

MAX_INVALID_INPUTS = 10

class CoreEngine(ABC):
    """
    Abstract Base Class for all Games.
    It manages the game loop state, history tracking, and basic lifecycle.
    """

    def __init__(self):
        self.game_status = GameStatus.RUNNING
        self.input_history: List[str] = []
        self.observation_history: List[str] = []
        self.consecutive_invalid_inputs = 0

    def start(self) -> str:
        """
        Initializes the game and returns the first observation.
        """
        initial_obs = self.get_initial_observation()
        self.observation_history.append(initial_obs)
        return initial_obs

    def step(self, input_data: str) -> str:
        """
        Advances the game by one turn.
        """
        self.input_history.append(input_data)

        try:
            self.verify_input(input_data)
            self.consecutive_invalid_inputs = 0
        except ValueError as e:
            self.consecutive_invalid_inputs += 1
            if self.consecutive_invalid_inputs >= MAX_INVALID_INPUTS:
                self.game_status = GameStatus.FAILED
                return "Too many invalid inputs. Aborting the game to avoid infinite loop."
            return str(e)
        
        new_obs = self.process_input(input_data)
        self.observation_history.append(new_obs)
        return new_obs
    
    def get_initial_observation(self) -> str:
        obs = f"Game '{self.name}' started.\n"
        obs += self.get_instructions()
        return obs
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Returns the name of the game."""
        ...

    @abstractmethod
    def get_instructions(self) -> str:
        """Returns the game instructions."""
        ...

    @abstractmethod
    def verify_input(self, input_data: str):
        if not isinstance(input_data, str):
            raise ValueError("Input must be a string.")

    @abstractmethod
    def process_input(self, input_data: str) -> str:
        ...

    def get_full_history(self) -> str:        
        """
        Formats the session history into a readable string.
        """
        out = []
        max_len = max(len(self.observation_history), len(self.input_history))
        
        for i in range(max_len):
            if i < len(self.observation_history):
                out.append(f"Observation {i}: {self.observation_history[i]}")
            if i < len(self.input_history):
                out.append(f"Input {i}: {self.input_history[i]}")
            out.append("-" * 20)
            
        return "\n".join(out)