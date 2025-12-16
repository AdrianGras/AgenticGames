import os
from abc import ABC, abstractmethod
from typing import List, Dict, AsyncGenerator, Any

class GeneralLLM(ABC):
    """
    Abstract Base Class for all LLM Client implementations.
    
    It handles:
    1. Secure credential loading from environment variables.
    2. Enforcing a standard interface for asynchronous streaming (stream_chat).
    """

    def __init__(self):
        """
        Initializes the LLM wrapper. 
        It automatically loads credentials and creates the client instance.
        """
        self.api_key = self._load_api_credentials()
        self.client = self.generate_client(self.api_key)

    def _load_api_credentials(self) -> str:
        """
        Loads API credentials from environment variables based on the specific implementation.
        
        Returns:
            str: The API key.
            
        Raises:
            ValueError: If the required environment variable is missing.
        """
        api_key_name = self.get_api_key_name()
        api_key = os.getenv(api_key_name)
        
        if not api_key:
            raise ValueError(f"API key for environment variable '{api_key_name}' not found.")
        
        return api_key
    
    @abstractmethod
    def get_api_key_name(self) -> str:
        """
        Returns the specific environment variable name for this provider.
        Example: 'OPENAI_API_KEY'
        """
        pass

    @abstractmethod
    def generate_client(self, api_key: str) -> Any:
        """
        Instantiates and returns the specific SDK client (e.g., AsyncOpenAI).
        
        Args:
            api_key (str): The loaded API key.
        """
        pass

    @abstractmethod
    async def stream_chat(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.7, 
        max_tokens: int = 150
    ) -> AsyncGenerator[str, None]:
        """
        Generates a streaming response from the LLM.

        Args:
            messages (List[Dict[str, str]]): The full history, including system prompt.
                                             Format: [{"role": "system", ...}, {"role": "user", ...}]
            temperature (float): Controls randomness (0.0 to 1.0).
            max_tokens (int): Limit for the response length.

        Yields:
            str: Individual string tokens as they are generated.
        """
        yield ""  