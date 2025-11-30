from abc import ABC, abstractmethod
import os
import json

class GeneralLLM(ABC):
    def __init__(self, system_prompt_id = "default"):
        super().__init__()
        api_key = self.load_api_credentials()
        self.client = self.generate_client(api_key)


    def load_api_credentials(self):
        """
        Loads API credentials from environment variables.
        """
        api_key = os.getenv(self.api_key_name)
        if not api_key:
            raise ValueError(f"API key for {self.api_key_name} not found in environment variables.")
        return api_key
    
    @abstractmethod
    @property
    def api_key_name(self):
        """
        Returns the name of the LLM model.
        """
        pass

    @abstractmethod
    def generate_client(self, api_key):
        """
        Generates and returns the LLM client using the provided API key.
        """
        pass

    @abstractmethod
    def chat_completion(self, message_history, system_prompt, temperature=0.7, max_tokens=150):
        """
        Generates a chat completion based on the message history and system prompt.
        """
        pass