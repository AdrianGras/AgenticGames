from typing import List, Any
import gradio as gr

from ui_layer.gradio.game_session.agent_views.agent_control_base_ui import AgentControlBaseUI

class StandardAgentUI(AgentControlBaseUI):
    """
    Concrete implementation of the Agent Control UI for text-based reasoning.
    
    This class renders a standard Textbox to display the agent's internal monologue.
    It maintains an internal state buffer to accumulate incoming tokens, 
    ensuring a continuous log history since Gradio updates overwrite previous content.
    """

    def __init__(self):
        """
        Initializes the UI component and the internal history buffer.
        """
        self._history_buffer: List[str] = []
        super().__init__()

    def _build_reasoning_layout(self) -> List[gr.Component]:
        """
        Constructs the specific layout for text-based reasoning.        
        Returns:
            List[gr.Component]: The list of components that will be targeted 
                                by the 'update' method (in this case, the log box).
        """
        with gr.Accordion("🧠 Agent Thoughts", open=True):
            self.log_box = gr.Markdown(
                value="*Waiting for agent to start...*",
                elem_classes=["game-log-container"],
                height=500, 
            )
        
        return [self.log_box]

    def update(self, new_tokens: List[Any]) -> Any:
        """
        Processes new reasoning tokens received from the backend.
        Args:
            new_tokens: A list of data chunks emitted by the agent. 
                        Can contain strings, integers, or other serializable objects.
                        
        Returns:
            str: The complete accumulated log string.
        """
        if not new_tokens:
            return gr.skip()
        
        new_chunk = "".join(str(token) for token in new_tokens)
        
        self._history_buffer.append(new_chunk)
        
        return "".join(self._history_buffer)