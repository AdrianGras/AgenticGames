import os
import json
from typing import List, Dict, Optional

from agent_layer.llm_agents.llm_agent import LLMAgent
from agent_layer.agent_actor import ReasoningCallback

class BasicAgent(LLMAgent):
    """
    A concrete implementation of an LLM Agent.
    
    It maintains a session memory (message history) and uses a predefined system prompt
    loaded from a JSON configuration file to guide the LLM's behavior.
    """

    def __init__(
        self, 
        model_name: str = "grok-4-1-fast-non-reasoning", 
        system_prompt_id: str = "check_hypothesis", 
        on_reasoning: Optional[ReasoningCallback] = None
    ):
        """
        Initialize the BasicAgent.

        Args:
            model_name (str): The identifier of the model to use (passed to LLMAgent).
            system_prompt_id (str): The key to look up in 'system_prompts.json'.
            on_reasoning (ReasoningCallback, optional): Hook for real-time UI streaming.
        """
        super().__init__(model_name=model_name, on_reasoning=on_reasoning)
        
        self.message_history: List[Dict[str, str]] = []
        self.system_prompt = self._load_system_prompt(system_prompt_id)

    def _load_system_prompt(self, system_prompt_id: str) -> str:
        """
        Loads the system prompt from the local 'system_prompts.json' file.

        Args:
            system_prompt_id (str): The ID key in the JSON file.

        Returns:
            str: The text content of the system prompt.

        Raises:
            FileNotFoundError: If 'system_prompts.json' is missing.
            ValueError: If the ID is not found in the JSON.
        """
        current_dir = os.path.dirname(__file__)
        prompt_path = os.path.join(current_dir, "system_prompts.json")
        
        if not os.path.exists(prompt_path):
            raise FileNotFoundError(f"System prompts file not found at: {prompt_path}")

        with open(prompt_path, 'r', encoding='utf-8') as f:
            prompts = json.load(f)

        if system_prompt_id not in prompts:
            raise ValueError(f"System prompt ID '{system_prompt_id}' not found.")
            
        return prompts[system_prompt_id]

    async def get_action(self, observation: str) -> str:
        """
        Processes the game observation and returns the next action.

        This method:
        1. Updates internal memory with the new observation.
        2. Streams the response from the LLM client (emitting reasoning to UI).
        3. Parses the final action command.

        Args:
            observation (str): The text description from the game environment.

        Returns:
            str: The parsed action command (e.g., "open door").
        """
        self.message_history.append({
            "role": "user", 
            "content": observation
        })
        
        messages = [{"role": "system", "content": self.system_prompt}] + self.message_history
        full_response = ""


        async for token in self.llm_client.stream_chat(messages):
            full_response += token
            await self.emit_reasoning(token)

        self.message_history.append({
            "role": "assistant", 
            "content": full_response
        })

        return self._extract_action(full_response)