import asyncio
from app_layer.io.input_source import InputSource

class AsyncInputBridge(InputSource):
    """
    Asynchronous bridge for human input using a single-slot synchronized buffer.
    
    This implementation uses a Queue with maxsize=1 to safely bridge the UI 
    and the Game Runner, preventing generator lifecycle errors.
    """
    def __init__(self):
        self._queue: asyncio.Queue[str] = asyncio.Queue(maxsize=1)

    async def get(self) -> str:
        """
        Awaits the next input from the buffer.
        """
        return await self._queue.get()

    def set_input(self, text: str) -> bool:
        """
        Attempts to deliver input to the bridge.
        
        Args:
            text: The input string from the UI.
            
        Returns:
            bool: True if the input was accepted into the buffer, 
                  False if the buffer is full (previous input not consumed).
        """
        try:
            self._queue.put_nowait(text)
            return True
        except asyncio.QueueFull:
            return False