from typing import List, Any
import gradio as gr
from ui_layer.gradio.game_session.agent_views.agent_control_base_ui import AgentControlBaseUI

class StandardAgentUI(AgentControlBaseUI):
    """
    UI implementation for displaying an agent's internal reasoning process.
    
    This class uses a gr.Chatbot component to achieve native autoscroll functionality
    without the visual overhead of a traditional chat interface. It utilizes a 
    'Single-Bubble' approach where all incoming tokens are appended to a single 
    continuous message.
    """

    def __init__(self):
        """
        Initializes the agent UI and the internal history buffer.
        
        The buffer starts with a single tuple [None, ""]. By setting the user 
        role to None, we hide the user bubble and only display the agent's 
        stream as a full-width block.
        """
        self._history_buffer: List[List[Any]] = [[None, ""]] 
        super().__init__()

    def _build_reasoning_layout(self) -> List[gr.Component]:
        """
        Constructs the reasoning log layout using a Chatbot component.
        
        The Chatbot is configured to look like a terminal/log window by hiding
        avatars and enabling full-width bubbles.

        Returns:
            List[gr.Component]: The reasoning log component.
        """
        with gr.Accordion("🧠 Agent Thoughts", open=True):
            self.log_box = gr.Chatbot(
                label="Reasoning Stream",
                value=self._history_buffer,
                height=500,
                show_label=False,
                type="tuples",
                avatar_images=(None, None),
                bubble_full_width=True,
                show_copy_button=True,
                render_markdown=True
            )
        return [self.log_box]

    def update(self, new_tokens: List[Any]) -> Any:
        """
        Appends new reasoning tokens to the existing single-message stream.

        This method updates the state of the first message in the buffer instead
        of creating new chat bubbles. This triggers the Chatbot's native 
        autoscroll for a seamless streaming experience.

        Args:
            new_tokens (List[Any]): Chunks of text or data emitted by the LLM.

        Returns:
            Any: The updated history buffer or gr.skip() if no data is provided.
        """
        if not new_tokens:
            return gr.skip()
        
        # Convert incoming tokens to a single string chunk
        new_chunk = "".join(str(token) for token in new_tokens)
        
        # Modify the existing agent message in the buffer (index 0, position 1)
        current_text = self._history_buffer[0][1]
        self._history_buffer[0][1] = current_text + new_chunk
        
        return self._history_buffer