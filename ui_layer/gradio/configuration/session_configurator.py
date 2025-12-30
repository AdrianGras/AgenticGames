import gradio as gr
from typing import List, Dict, Any, Tuple, Optional

from ui_layer.gradio.signals import SignalEmitter
from ui_layer.gradio.layout_utils import TightCenteredLayout, VSpacer

from app_layer.session_config import SessionConfig
from app_layer.registries.manager import get_game_registry, get_agent_registry
from .widget_factory import create_widget

class SessionConfigurator(SignalEmitter):
    """
    Configurador de UI dinámico que sincroniza con los registros de dominio.
    Utiliza un mapeo ID-Componente basado en clausuras para garantizar la integridad
    de los datos en entornos reactivos.
    """

    def __init__(self):
        super().__init__()
        
        # 1. Acceso a Registros
        self.game_reg = get_game_registry()
        self.agent_reg = get_agent_registry()
        game_ids = self.game_reg.list_ids()

        with TightCenteredLayout():
            with gr.Column():
                gr.Markdown("## ⚙️ Configuración de Sesión")
                
                # --- Selectores de Nivel Superior ---
                with gr.Row():
                    self.dd_game = gr.Dropdown(
                        choices=game_ids, 
                        label="Juego", 
                        value=game_ids[0] if game_ids else None
                    )
                    self.rb_mode = gr.Radio(
                        choices=["User", "Agent"], 
                        value="User", 
                        label="Modo de Juego"
                    )

                # --- Área de Configuración Dinámica ---
                @gr.render(inputs=[self.dd_game, self.rb_mode])
                def render_config_form(game_id, mode):
                    if not game_id:
                        gr.Warning("No hay juegos registrados.")
                        return
                    
                    game_manifest = self.game_reg.get(game_id)
                    is_agent_mode = (mode == "Agent")
                    
                    # Listas de rastreo locales al renderizado actual
                    current_ids: List[str] = ["game_id", "mode"]
                    current_components: List[gr.Component] = [self.dd_game, self.rb_mode]

                    # 1. Parámetros del Juego
                    if game_manifest.params:
                        gr.Markdown(f"### 🎮 Ajustes de {game_manifest.display_name}")
                        for spec in game_manifest.params:
                            comp = create_widget(spec)
                            current_ids.append(spec.id)
                            current_components.append(comp)
                    
                    # 2. Lógica de Agente (Reactividad Anidada)
                    if is_agent_mode:
                        VSpacer(10)
                        gr.Markdown("---")
                        gr.Markdown("### 🤖 Configuración del Agente")
                        
                        agent_ids = self.agent_reg.list_ids()
                        agent_id_comp = gr.Dropdown(
                            choices=agent_ids, 
                            label="Estrategia del Agente",
                            value=agent_ids[0] if agent_ids else None
                        )
                        
                        @gr.render(inputs=[agent_id_comp])
                        def render_agent_params(selected_agent_id):
                            if not selected_agent_id: return
                            
                            # Copiamos el estado actual para este sub-render
                            local_ids = list(current_ids)
                            local_components = list(current_components)
                            
                            # Añadimos el selector de agente
                            local_ids.append("agent_id")
                            local_components.append(agent_id_comp)
                            
                            # Añadimos parámetros específicos del agente
                            agent_manifest = self.agent_reg.get(selected_agent_id)
                            for spec in agent_manifest.params:
                                comp = create_widget(spec)
                                local_ids.append(spec.id)
                                local_components.append(comp)

                            self._build_submit_section(local_ids, local_components)
                    else:
                        # Modo Humano: Botón directo
                        self._build_submit_section(current_ids, current_components)

    def _build_submit_section(self, ids: List[str], components: List[gr.Component]):
        """Crea el botón de inicio y vincula el evento capturando los IDs actuales."""
        VSpacer(20)
        btn_start = gr.Button("🚀 Inicializar Sesión", variant="primary", size="lg")

        # Clausura: 'ids' queda capturado en el scope de esta función
        def handle_click(*values):
            # Emparejamos IDs con Valores reales de la UI
            tagged_data = list(zip(ids, values))
            return self._pack_configuration(tagged_data)

        self._send_on(
            event_trigger=btn_start.click,
            inputs=components,
            fn_process=handle_click
        )

    def _pack_configuration(self, tagged_data: List[Tuple[str, Any]]) -> SessionConfig:
        """Transforma las tuplas etiquetadas en el objeto de dominio SessionConfig."""
        data = dict(tagged_data)
        
        game_id = data.get("game_id")
        is_human = (data.get("mode") == "User")
        agent_id = data.get("agent_id")

        # Extraer parámetros según manifiesto
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