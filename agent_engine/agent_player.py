from abc import ABC, abstractmethod

class AgentPlayer(ABC):
    def __init__(self, LLM_model):
        super().__init__()
        self.LLM_model = LLM_model


    @abstractmethod
    def get_action(self, game_observation):
        """
        Given the current game observation, returns the next action to take.
        """
        pass