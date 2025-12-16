import asyncio
from agent_layer.actor import Actor

class HumanActor(Actor):
    """
    An implementation of Actor driven by human input via an asynchronous queue.
    
    This class is designed to work with event-driven UIs (like Gradio), 
    halting execution until user input is received in the queue.
    """

    def __init__(self, input_queue: asyncio.Queue):
        """
        Initialize the HumanActor.

        Args:
            input_queue (asyncio.Queue): The shared queue where the UI pushes user commands.
        """
        self.input_queue = input_queue

    async def get_action(self, observation: str) -> str:
        """
        Waits asynchronously for human input from the queue.
        """
        # The execution pauses here without blocking the main thread 
        # until the UI puts a string into the queue.
        action = await self.input_queue.get()
        return action