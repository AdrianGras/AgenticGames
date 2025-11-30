
from LLMs.general_llm import GeneralLLM
import openai

class OpenAILLM(GeneralLLM):
    def __init__(self, model_name="gpt-4"):
        self.model_name = model_name
        super().__init__()

    @property
    def api_key_name(self):
        return "OPENAI_API_KEY"

    def generate_client(self, api_key):
        openai.api_key = api_key
        return openai

    def chat_completion(self, message_history, system_prompt, temperature=0.7, max_tokens=150):
        messages = [{"role": "system", "content": system_prompt}]
        messages += message_history
        

        response = self.client.ChatCompletion.create(
            model=self.model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message['content']