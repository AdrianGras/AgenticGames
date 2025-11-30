from agent_layer.agents.basic_agent.basic_agent import BasicAgent

AGENTS = {
    "basic_agent": BasicAgent,
}

def get_agent(agent_name, llm):
    if agent_name not in AGENTS:
        raise ValueError(f"Agent '{agent_name}' not found.")

    return AGENTS.get(agent_name)(llm)

def list_available_agents():
    return list(AGENTS.keys())