import asyncio
from typing import Protocol
from agent_layer.actor import Actor

class InputSource(Protocol):
    """
    Interface definition for any object capable of providing input strings asynchronously.
    
    This protocol allows HumanActor to be decoupled from specific implementations 
    like asyncio.Queue or CLI input handlers.
    """
    async def get(self) -> str:
        """
        Asynchronously retrieves the next input string.
        """
        ...

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