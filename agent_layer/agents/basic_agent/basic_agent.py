import os
from agent_layer.agents.agent_player import AgentPlayer
import json

class BasicAgent(AgentPlayer):
    def __init__(self, llm, system_prompt_id="check_hypothesis"):
        super().__init__(llm)
        self.message_history = []
        self.system_prompt = self.load_system_prompt(system_prompt_id)

    def load_system_prompt(self, system_prompt_id):
        """
        Loads the system prompt based on the provided ID.
        """
        current_dir = os.path.dirname(__file__)
        prompt_path = os.path.join(current_dir, "system_prompts.json")
        with open(prompt_path, 'r') as f:
            prompts = json.load(f)
        if not system_prompt_id in prompts:
            raise ValueError(f"System prompt ID '{system_prompt_id}' not found.")
        return prompts[system_prompt_id]

    def get_action(self, game_observation):
        """
        Given the current game observation, returns the next action to take.
        """
        self.message_history.append({
            "role": "user",
            "content": game_observation
        })

        response = self.LLM_model.chat_completion(
            message_history=self.message_history,
            system_prompt=self.system_prompt
        )

        self.message_history.append({
            "role": "assistant",
            "content": response
        })
        action = self.parse_action(response)
        return action