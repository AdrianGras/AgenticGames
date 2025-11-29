from abc import ABC, abstractmethod
import os

class GeneralLLM(ABC):
    def __init__(self):
        super().__init__()
        self.api_key = self.load_api_credentials()


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

    