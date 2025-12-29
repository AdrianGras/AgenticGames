import gradio as gr
from typing import Optional
import uuid

from ui_layer.gradio.configuration.session_configurator import SessionConfigurator
from ui_layer.gradio.game_session.game_session_ui import GameSessionUI
from ui_layer.gradio.layout_utils import AppWindow

from app_layer.session_config import SessionConfig

class GradioApp:
    """
    Main Application Entry Point.
    Orchestrates the transition between configuration and active gameplay.
    """

    def build(self) -> gr.Blocks:
        with AppWindow(title="Agentic Games") as demo:            
            gr.Markdown("# 🎮 Agentic Games")

            self.session_config = gr.State(value=None)
            self.render_key = gr.State(value=None)
            with gr.Column() as self.config_panel:
                self.configurator = SessionConfigurator()

            @gr.render(inputs=[self.session_config, self.render_key])
            def render_active_session(config: Optional[SessionConfig], _key: str):
                if config is None:
                    return
                GameSessionUI(config)

            def start_session(config: SessionConfig):
                """
                Triggered when the configurator emits a valid SessionConfig.
                1. Returns the config and a new UUID to the states.
                2. Updates the config_panel to be invisible.
                """
                return (
                    config, 
                    str(uuid.uuid4()), 
                    gr.update(visible=False)
                )

            self.configurator.on_signal(
                fn=start_session,
                outputs=[
                    self.session_config, 
                    self.render_key, 
                    self.config_panel
                ]
            )

        return demo