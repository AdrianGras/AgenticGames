from abc import ABC, abstractmethod
from concurrent.futures import Future
from typing import Iterator, Any, Tuple


class AgentPlayer(ABC):
    def __init__(self, LLM_model: Any):
        super().__init__()
        self.LLM_model = LLM_model

    @abstractmethod
    def get_action(self, game_observation: Any) -> Any:
        """
        Given the current game observation, returns the next action to take.
        """
        pass

    def get_future_action(
        self, game_observation: Any
    ) -> Tuple[Iterator[str], Future]:
        """
        Naive default implementation:
        - Empty reasoning stream
        - Future resolved immediately with get_action result
        """

        def empty_reasoning_stream() -> Iterator[str]:
            if False:
                yield ""  # hace que sea un generator válido

        action = self.get_action(game_observation)

        action_future: Future = Future()
        action_future.set_result(action)

        return empty_reasoning_stream(), action_future


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