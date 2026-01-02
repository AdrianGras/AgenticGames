import asyncio
from typing import Protocol
from agent_layer.actor import Actor
from app_layer.input_source import InputSource


class HumanActor(Actor):
    """
    An implementation of Actor driven by human input via an asynchronous source.
    
    This class halts execution until user input is received from the provided 
    input source, making it compatible with both blocking CLI environments 
    and event-driven UIs.
    """

    def __init__(self, input_queue: InputSource):
        """
        Initialize the HumanActor.

        Args:
            input_queue (InputSource): An object implementing the InputSource protocol 
                                       (must have an async .get() method).
        """
        self.input_queue = input_queue

    async def get_action(self, observation: str) -> str:
        """
        Waits asynchronously for human input from the source.

        Args:
            observation (str): The current game state (displayed to the user by the UI).

        Returns:
            str: The action command entered by the human.
        """
        action = await self.input_queue.get()
        return action