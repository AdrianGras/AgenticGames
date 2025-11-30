from abc import ABC, abstractmethod
import os
import json

class GeneralLLM(ABC):
    def __init__(self):
        super().__init__()
        api_key = self.load_api_credentials()
        self.client = self.generate_client(api_key)


    def load_api_credentials(self):
        """
        Loads API credentials from environment variables.
        """
        api_key_name = self.get_api_key_name()
        api_key = os.getenv(api_key_name)
        if not api_key:
            raise ValueError(f"API key for {api_key_name} not found in environment variables.")
        return api_key
    
    @abstractmethod
    def get_api_key_name(self):
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
        Args:
            message_history (list): List of dicts with 'role' and 'content' keys.
            system_prompt (str): System instructions for the LLM.
            temperature (float): Sampling temperature.
            max_tokens (int): Maximum tokens in the response.
        
        Returns:
            str: The generated response from the LLM.
        """
        pass