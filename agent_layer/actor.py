from abc import ABC, abstractmethod

class Actor(ABC):
    """
    Abstract Base Class representing any entity capable of playing the game.
    
    This interface unifies Human players (via UI) and AI Agents (via LLMs/Policies),
    allowing the orchestration layer to treat them interchangeably.
    """

    @abstractmethod
    async def get_action(self, observation: str) -> str:
        """
        Processes the incoming observation and determines the next action.

        Args:
            observation (str): The text description provided by the game environment.

        Returns:
            str: The action to be executed in the game.
        """
        pass