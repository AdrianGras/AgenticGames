import asyncio
from typing import Optional

from agent_layer.human_actor import InputSource

class AsyncInputBridge(InputSource):
    """
    Asynchronous bridge for human input, allowing non-blocking interaction
    """
    def __init__(self):
        self._pending_future: Optional[asyncio.Future[str]] = None

    async def get(self) -> str:
        """
        Awaits input from an external source via the set_input method.
        Returns:
            str: The input text provided by the user.
        """
        loop = asyncio.get_running_loop()
        self._pending_future = loop.create_future()
        
        try:
            return await self._pending_future
        finally:
            self._pending_future = None

    def set_input(self, text: str) -> bool:
        """
        Sets the input text, fulfilling the pending future if it exists.
        Args:
            text (str): The input text to be provided.
        Returns:
            bool: True if the input was successfully set, False otherwise.
        """
        if self._pending_future is not None and not self._pending_future.done():
            self._pending_future.set_result(text)
            return True
        return False