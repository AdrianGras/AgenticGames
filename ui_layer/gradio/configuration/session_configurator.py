import gradio as gr
from typing import List, Optional

from ui_layer.gradio.signals import SignalEmitter
from ui_layer.gradio.layout_utils import TightCenteredLayout, VSpacer, HSpacer

from app_layer.session_config import SessionConfig

from game_layer.games.game_selector import list_available_games
from agent_layer.agent_selector import list_available_agents
from agent_layer.llm_agents.LLMs.llm_selector import list_available_llms

class SessionConfigurator(SignalEmitter):
    """
    UI Component responsible for configuring and validating session parameters.

    Uses CenteredLayout to render a focused, centered configuration card.
    """

    def __init__(self):
        """
        Initializes the configuration UI and wires internal signals.
        """
        super().__init__()
        
        with TightCenteredLayout():
            with gr.Column():
                gr.Markdown("## ⚙️ Session Setup")
                VSpacer(20)
                
                # --- Game Section ---
                gr.Markdown("### 📺🕹️ Game Configuration")
                with gr.Row():
                    game_list = list_available_games()
                    self.dd_game = gr.Dropdown(
                        choices=game_list,
                        label="Select Game",
                        value=game_list[0] if game_list else None,
                        interactive=True
                    )
                    self.rb_mode = gr.Radio(
                        choices=["User", "Agent"], 
                        value="User", 
                        label="Play Mode",
                        interactive=True
                    )

                VSpacer(20)

                # --- Agent Section (Conditional) ---
                with gr.Group(visible=False) as self.agent_group:
                    gr.Markdown("### 🤖 Agent Configuration")
                    VSpacer(10)
                    with gr.Row():
                        agent_list = list_available_agents()
                        self.dd_agent = gr.Dropdown(
                            choices=agent_list, 
                            value=agent_list[0] if agent_list else None,
                            label="Strategy",
                            interactive=True
                        )
                        
                        llm_list = list_available_llms()
                        self.dd_model = gr.Dropdown(
                            choices=llm_list,
                            value=llm_list[0] if llm_list else None,
                            label="LLM Model",
                            interactive=True
                        )

                VSpacer(20)
                self.btn_start = gr.Button("🚀 Initialize Session", variant="primary", size="lg")

        # --- UI Logic ---
        self.rb_mode.change(
            fn=lambda mode: gr.update(visible=(mode == "Agent")), 
            inputs=self.rb_mode, 
            outputs=self.agent_group
        )

        # --- Signal Wiring ---
        self._send_on(
            event_trigger=self.btn_start.click,
            inputs=[self.dd_game, self.rb_mode, self.dd_agent, self.dd_model],
            fn_process=self._pack_configuration
        )

    def _pack_configuration(self, game: str, mode: str, agent: str, model: str) -> SessionConfig:
        """
        Validates inputs and packs them into a SessionConfig object.
        """
        if not game:
            raise gr.Error("Please select a game to proceed.")
        
        is_human = (mode == "User")
        agent_params = None

        if not is_human:
            if not agent: raise gr.Error("Select an Agent Strategy.")
            if not model: raise gr.Error("Select an LLM Model.")
            agent_params = {"model_name": model}

        return SessionConfig(
            game_name=game,
            is_human=is_human,
            agent_name=agent if not is_human else None,
            game_params={}, 
            agent_params=agent_params
        )