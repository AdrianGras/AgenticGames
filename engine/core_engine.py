from abc import ABC, abstractmethod
from enum import Enum, auto

class GameStatus(Enum):
    RUNNING = auto()
    FINISHED = auto()
    FAILED = auto()

class CoreEngine(ABC):
    def __init__(self):
        self.game_status = GameStatus.RUNNING
        self.input_history = []
        self.observation_history = []

    def start(self):
        initial_obs = self.get_initial_observation()
        self.observation_history.append(initial_obs)
        return initial_obs

    def step(self, input_data):
        self.input_history.append(input_data)
        self.verify_input(input_data)
        new_obs = self.process_input(input_data)
        self.observation_history.append(new_obs)
        return new_obs
    
    def get_initial_observation(self):
        """
        Returns the initial observation presented to the user.
        """

        initial_obs = f"Game {self.name} started"
        initial_obs += "\n" + self.get_instructions()
        return initial_obs
    
    @property
    @abstractmethod
    def name(self):
        """
        Returns the name of the game.
        """
        return "Template Game"

    @abstractmethod
    def get_instructions(self):
        """
        Returns the game instructions.
        """
        return f"Insert game instructions here."

    @abstractmethod
    def verify_input(self, input_data):
        """
        Validates the input.
        """
        assert isinstance(input_data, str), "Input data must be a string"

    @abstractmethod
    def process_input(self, input_data):
        """
        Produces a new observation after receiving input.
        """
        return "Template observation after processing input."


    def print_observations(self, n_last=5):
        """
        Prints the last recorded observations.
        """
        print(f"== Observations for {self.name} ==")
        for i, obs in enumerate(self.observation_history[-n_last:], start=1):
            print(f"{i}. {obs}")

    def get_game_status(self):
        """
        Returns the current game status.
        """
        return self.game_status