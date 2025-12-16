from openai import AsyncOpenAI
from agent_layer.llm_agents.LLMs.openai_llm import OpenAILLM

class GrokLLM(OpenAILLM):
    """
    Concrete implementation for xAI's Grok models.
    
    Since Grok offers an API that is fully compatible with the OpenAI SDK,
    this class inherits from OpenAILLM and simply redirects the client 
    to the xAI base URL.
    """

    def __init__(self, model_name: str = "grok-beta"):
        """
        Args:
            model_name (str): The specific Grok model identifier (e.g., 'grok-beta').
        """
        super().__init__(model_name=model_name)

    def get_api_key_name(self) -> str:
        """
        Specifies the environment variable name expected for xAI.
        """
        return "XAI_API_KEY"

    def generate_client(self, api_key: str) -> AsyncOpenAI:
        """
        Initializes the asynchronous OpenAI client pointing to xAI's infrastructure.
        """
        return AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.x.ai/v1"
        )