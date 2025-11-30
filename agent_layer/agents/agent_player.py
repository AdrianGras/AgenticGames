from abc import ABC, abstractmethod
import re

class AgentPlayer(ABC):
    def __init__(self, LLM_model):
        super().__init__()
        self.LLM_model = LLM_model


    @abstractmethod
    def get_action(self, game_observation):
        """
        Given the current game observation, returns the next action to take.
        """
        pass

    def parse_action(self, action_str):
        """
        Parses the action string to extract the action command safely.
        Accepts formats like:
        - action:{...}
        - action: {...}
        - Action: {...}
        - ACTION: { ... }
        """
        pattern = r'action\s*:\s*\{(.*?)\}'
        match = re.search(pattern, action_str, flags=re.IGNORECASE | re.DOTALL)

        if not match:
            raise ValueError(f"Could not parse action from response: {action_str}")

        action = match.group(1).strip()

        return action