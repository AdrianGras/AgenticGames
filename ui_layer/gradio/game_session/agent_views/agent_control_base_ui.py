import gradio as gr
from abc import abstractmethod
from typing import List

from ui_layer.gradio.signals import SignalEmitter, SignalReceiver
from ui_layer.gradio.game_session.agent_views.agent_comand import AgentCommand

class AgentControlBaseUI(SignalEmitter, SignalReceiver):
    """
    Abstract Base Class for Agent Control Interfaces using the Template Method pattern.

    This component standardizes the flow control mechanism (Play, Pause, Step) 
    across all agent types while delegating the visualization of internal 
    reasoning (text, graphs, etc.) to concrete subclasses.

    Inheritance:
        - SignalEmitter: To dispatch flow control commands (AgentCommand).
        - SignalReceiver: To receive and display streaming reasoning data.
    """

    def __init__(self):
        """
        Initializes the component structure, renders the common control toolbar,
        and binds the flow control events.
        """
        SignalEmitter.__init__(self)

        with gr.Group():
            gr.Markdown("### 🤖 Agent Controller")

            # --- Specific Reasoning View (Template Hook) ---
            self.reasoning_targets = self._build_reasoning_layout()

            # --- Common Control Toolbar ---
            with gr.Row():
                self.btn_step = gr.Button("⏯️ Step Next", variant="primary", visible=True)
                self.btn_play = gr.Button("▶️ Run Loop", visible=True)
                self.btn_pause = gr.Button("⏸️ Stop Loop", variant="stop", visible=False)

        # --- Button Visibility Logic ---
        
        # When PLAY is pressed: Hide Step/Play, Show Pause
        self.btn_play.click(
            fn=lambda: (gr.update(visible=False), gr.update(visible=False), gr.update(visible=True)),
            inputs=None,
            outputs=[self.btn_step, self.btn_play, self.btn_pause]
        )

        # When PAUSE (Stop) is pressed: Show Step/Play, Hide Pause
        self.btn_pause.click(
            fn=lambda: (gr.update(visible=True), gr.update(visible=True), gr.update(visible=False)),
            inputs=None,
            outputs=[self.btn_step, self.btn_play, self.btn_pause]
        )

        # --- Signal Wiring (Domain Logic) ---
        self._send_on(
            event_trigger=self.btn_step.click, 
            inputs=None, 
            fn_process=lambda: AgentCommand.STEP
        )
        
        self._send_on(
            event_trigger=self.btn_play.click, 
            inputs=None, 
            fn_process=lambda: AgentCommand.PLAY
        )
        
        self._send_on(
            event_trigger=self.btn_pause.click, 
            inputs=None, 
            fn_process=lambda: AgentCommand.PAUSE
        )

        # 2. Initialize the Inbox (Receiver) capability with the specific targets
        SignalReceiver.__init__(self, targets=self.reasoning_targets)

    @abstractmethod
    def _build_reasoning_layout(self) -> List[gr.Component]:
        """
        Abstract hook to define the layout for the agent's internal state.

        Concrete subclasses must implement this method to instantiate the 
        specific Gradio components (e.g., Textbox, Plot, JSON) required 
        to visualize the agent's reasoning.

        Returns:
            List[gr.Component]: A list of Gradio components that will be 
                                updated by the `update` method when data arrives.
        """
        pass