from typing import Type, Any, Dict
from ui_layer.gradio.game_session.agent_views.standard_agent_ui import StandardAgentUI
from ui_layer.gradio.game_session.agent_views.agent_control_base_ui import AgentControlBaseUI

# Registry mapping agent identifiers to their respective UI implementations.
# All registered classes must inherit from AgentControlBaseUI to ensure 
# compatibility with flow control (Play/Pause/Step) and reasoning signals.
AGENT_UIs: Dict[str, Type[AgentControlBaseUI]] = {
    # "specialized_agent": SpecializedAgentUI,
}

def get_agent_ui(
    agent_name: str, 
    **kwargs: Any
) -> AgentControlBaseUI:
    """
    Factory function to instantiate the appropriate Agent UI component.

    Args:
        agent_name: The identifier of the agent strategy (e.g., 'basic_agent').
        **kwargs: Initialization arguments passed directly to the UI component 
                  constructor.

    Returns:
        AgentControlBaseUI: An instance of a specialized Agent UI component. 
                            Returns StandardAgentUI (Chatbot-based) as a fallback 
                            if the agent_name is not found in the registry.
    """
    # Fallback logic: if the agent doesn't have a specialized UI, 
    # we use the standard streaming reasoning implementation.
    if agent_name not in AGENT_UIs:
        return StandardAgentUI(**kwargs)
        
    ui_class = AGENT_UIs[agent_name]
    return ui_class(**kwargs)