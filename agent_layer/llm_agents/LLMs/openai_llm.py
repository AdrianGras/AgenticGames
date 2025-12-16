from typing import List, Dict, AsyncGenerator, Any
from openai import AsyncOpenAI

from agent_layer.llm_agents.LLMs.general_llm import GeneralLLM

class OpenAILLM(GeneralLLM):
    """
    Concrete implementation of GeneralLLM for OpenAI models (GPT-3.5, GPT-4, etc).
    """

    def __init__(self, model_name: str = "gpt-4-turbo"):
        """
        Args:
            model_name (str): The specific OpenAI model identifier (e.g., 'gpt-4o', 'gpt-3.5-turbo').
        """
        super().__init__()
        self.model_name = model_name


    def get_api_key_name(self) -> str:
        """
        Specifies the environment variable name expected for OpenAI.
        """
        return "OPENAI_API_KEY"

    def generate_client(self, api_key: str) -> AsyncOpenAI:
        """
        Initializes the asynchronous OpenAI client.
        """
        return AsyncOpenAI(api_key=api_key)

    async def stream_chat(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.7, 
        max_tokens: int = 1000
    ) -> AsyncGenerator[str, None]:
        """
        Creates a streaming chat completion request to the OpenAI API.

        Args:
            messages (List[Dict]): The conversation history.
            temperature (float): Sampling temperature.
            max_tokens (int): Maximum tokens for the response.

        Yields:
            str: Tokens as they are received from the API.
        """
        # Initiate the request with stream=True
        stream = await self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=temperature,
            max_completion_tokens=max_tokens,
            stream=True
        )

        # Iterate over the asynchronous stream
        async for chunk in stream:
            # Extract content delta (can be None for the first/last chunks)
            content = chunk.choices[0].delta.content
            if content:
                yield content