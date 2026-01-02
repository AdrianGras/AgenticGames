import gradio as gr
from typing import List, Any, Tuple, Optional

from ui_layer.gradio.signals import SignalEmitter
from ui_layer.gradio.layout_utils import TightCenteredLayout, VSpacer

from app_layer.building.session_config import SessionConfig
from app_layer.registries.manager import get_game_registry, get_agent_registry
from .widget_factory import create_widget

class SessionConfigurator(SignalEmitter):
    """
    Dynamic UI Configurator that synchronizes with domain registries.
    Handles reactive form rendering for game and agent parameters.
    """

    def __init__(self):
        super().__init__()
        
        self.game_reg = get_game_registry()
        self.agent_reg = get_agent_registry()
        
        game_ids = self.game_reg.list_ids()
        agent_ids = self.agent_reg.list_ids()

        with TightCenteredLayout():
            with gr.Column():
                gr.Markdown("## ⚙️ Session Configuration")
                
                with gr.Row():
                    self.dd_game = gr.Dropdown(
                        choices=game_ids, 
                        label="Game", 
                        value=game_ids[0] if game_ids else None
                    )
                    self.rb_mode = gr.Radio(
                        choices=["User", "Agent"], 
                        value="User", 
                        label="Play Mode"
                    )

                # State to track agent selection across renders to avoid nested contexts
                self.selected_agent = gr.State(value=agent_ids[0] if agent_ids else None)

                @gr.render(inputs=[self.dd_game, self.rb_mode, self.selected_agent])
                def render_configuration_panel(game_id, mode, current_agent_id):
                    if not game_id:
                        gr.Warning("No games registered in the system.")
                        return
                    
                    is_agent_mode = (mode == "Agent")
                    active_ids: List[str] = ["game_id", "mode"]
                    active_components: List[gr.Component] = [self.dd_game, self.rb_mode]

                    # 1. Game Parameters
                    game_manifest = self.game_reg.get(game_id)
                    if game_manifest.params:
                        gr.Markdown(f"### 🎮 {game_manifest.display_name} Settings")
                        for spec in game_manifest.params:
                            comp = create_widget(spec)
                            active_ids.append(spec.id)
                            active_components.append(comp)
                    
                    # 2. Agent Configuration
                    if is_agent_mode:
                        VSpacer(10)
                        gr.Markdown("---")
                        gr.Markdown("### 🤖 Agent Configuration")
                        
                        agent_selector = gr.Dropdown(
                            choices=agent_ids, 
                            label="Agent Strategy",
                            value=current_agent_id
                        )
                        
                        # Trigger re-render when agent selection changes via state update
                        agent_selector.change(
                            fn=lambda x: x, 
                            inputs=[agent_selector], 
                            outputs=[self.selected_agent]
                        )
                        
                        active_ids.append("agent_id")
                        active_components.append(agent_selector)

                        if current_agent_id:
                            agent_manifest = self.agent_reg.get(current_agent_id)
                            for spec in agent_manifest.params:
                                comp = create_widget(spec)
                                active_ids.append(spec.id)
                                active_components.append(comp)

                    self._build_submit_section(active_ids, active_components)

    def _build_submit_section(self, ids: List[str], components: List[gr.Component]):
        """
        Creates the initialization button and binds the click event 
        mapping UI components to their respective IDs.
        """
        VSpacer(20)
        btn_start = gr.Button("🚀 Initialize Session", variant="primary", size="lg")

        def handle_click(*values):
            tagged_data = list(zip(ids, values))
            return self._pack_configuration(tagged_data)

        self._send_on(
            event_trigger=btn_start.click,
            inputs=components,
            fn_process=handle_click
        )

    def _pack_configuration(self, tagged_data: List[Tuple[str, Any]]) -> SessionConfig:
        """
        Transforms tagged UI data into a SessionConfig domain object.
        """
        data = dict(tagged_data)
        
        game_id = data.get("game_id")
        is_human = (data.get("mode") == "User")
        agent_id = data.get("agent_id")

        game_manifest = self.game_reg.get(game_id)
        game_params = {s.id: data.get(s.id) for s in game_manifest.params}

        agent_params = {}
        if not is_human and agent_id:
            agent_manifest = self.agent_reg.get(agent_id)
            agent_params = {s.id: data.get(s.id) for s in agent_manifest.params}

        return SessionConfig(
            game_name=game_id,
            is_human=is_human,
            agent_name=agent_id,
            game_params=game_params,
            agent_params=agent_params
        )