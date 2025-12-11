from agent_layer.LLMs.openai_llm import OpenAILLM
from openai import OpenAI

class GrokLLM(OpenAILLM):
    def __init__(self, model_name="grok-4"):
        super().__init__(model_name=model_name)

    def get_api_key_name(self):
        return "XAI_API_KEY"

    def generate_client(self, api_key):
        return OpenAI(
            api_key=api_key,
            base_url="https://api.x.ai/v1"
        )
