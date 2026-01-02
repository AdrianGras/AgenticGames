from typing import Protocol

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