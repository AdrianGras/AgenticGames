
from agent_layer.LLMs.general_llm import GeneralLLM
import openai

class OpenAILLM(GeneralLLM):
    def __init__(self, model_name="gpt-4.1"):
        self.model_name = model_name
        super().__init__()

    def get_api_key_name(self):
        return "OPENAI_API_KEY"

    def generate_client(self, api_key):
        openai.api_key = api_key
        return openai

    def chat_completion(self, message_history, system_prompt, temperature=0.7, max_tokens=1000):
        messages = [{"role": "system", "content": system_prompt}]
        messages += message_history
        
        response = ""
        attempts = 0
        while response == "" and attempts < 5:
            api_answer = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                #temperature=temperature,
                #max_completion_tokens=max_tokens
            )
            response = api_answer.choices[0].message.content
            attempts += 1

        if response == "":
            raise RuntimeError("Failed to get response from OpenAI API after multiple attempts.")

        return response