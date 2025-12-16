from typing import List, Type, Optional, Any
from agent_layer.agent_actor import AgentActor, ReasoningCallback
from agent_layer.llm_agents.basic_agent.basic_agent import BasicAgent

AGENTS: dict[str, Type[AgentActor]] = {
    "basic_agent": BasicAgent,
}

def get_agent(
    agent_id: str, 
    **kwargs: Any
) -> AgentActor:
    """
    Factory function to instantiate an Agent.

    Args:
        agent_id (str): The identifier of the agent logic (e.g., 'basic_agent').
        **kwargs: Additional arguments specific to certain agents (e.g., system_prompt_id).

    Returns:
        AgentActor: An instantiated agent ready to play.

    Raises:
        ValueError: If the agent_id is unknown.
    """
    if agent_id not in AGENTS:
        raise ValueError(
            f"Agent '{agent_id}' not found. "
            f"Available agents: {list_available_agents()}"
        )

    agent_class = AGENTS[agent_id]

    return agent_class(**kwargs)

def list_available_agents() -> List[str]:
    """
    Returns a list of registered agent identifiers.
    """
    return list(AGENTS.keys())