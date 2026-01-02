import asyncio
import gradio as gr
import uuid
from typing import List, Optional, Any, Union

from app_layer.building.session_config import SessionConfig
from app_layer.execution.managers.controlled_execution_manager import ControlledExecutionManager

from ui_layer.gradio.game_session.game_views.game_ui_selector import get_game_ui
from ui_layer.gradio.game_session.input_views.input_ui_selector import get_input_ui
from ui_layer.gradio.game_session.agent_views.agent_ui_selector import get_agent_ui
from ui_layer.gradio.game_session.agent_views.agent_control_base_ui import AgentControlBaseUI
from ui_layer.gradio.game_session.agent_views.standard_agent_ui import StandardAgentUI
from ui_layer.gradio.game_session.agent_views.agent_comand import AgentCommand
from ui_layer.gradio.signals import SignalEmitter, SignalReceiver
from ui_layer.gradio.layout_utils import WideCenteredLayout, HSpacer

class GameSessionUI:
    """
    Orchestrates the live Game Session View by bridging the ControlledExecutionManager 
    with polymorphic UI components.
    """

    def __init__(self, config: SessionConfig):
        """
        Initializes the session UI, logic manager, and lifecycle timers.
        """
        self.config = config
        self.manager = ControlledExecutionManager(config)
        
        self._build_layout()
        
        # Initial one-shot timer to start the background engine
        self.boot_timer = gr.Timer(value=0.1, active=True)
        
        self._setup_wiring()

    def _build_layout(self):
        """
        Defines the visual grid and instantiates the control mode (Human vs Agent).
        """
        with WideCenteredLayout():
            with gr.Row():
                with gr.Column(scale=4):
                    self.game_view: SignalReceiver = get_game_ui(self.config.game_name)

                HSpacer(20)
                
                with gr.Column(scale=4):
                    if self.config.is_human:
                        self.control_ui = get_input_ui(self.config.game_name)
                    else:
                        self.control_ui = get_agent_ui(self.config.agent_name)

        # Dual-channel reactive pipeline states
        self.game_buffer = gr.State()
        self.game_trigger = gr.State(0) 

        self.reasoning_buffer = gr.State()
        self.reasoning_trigger = gr.State(0)

        self.refresh_timer = gr.Timer(0.5, active=True)

    def _setup_wiring(self):
        """
        Connects lifecycle, data polling, and command dispatching.
        """
        # A. Lifecycle
        self.boot_timer.tick(
            fn=self._kickstart_manager,
            inputs=None,
            outputs=[self.boot_timer]
        )

        # B. Unified Polling (Timer -> States)
        self.refresh_timer.tick(
            fn=self._poll_everything,
            inputs=None,
            outputs=[
                self.game_buffer, self.game_trigger,
                self.reasoning_buffer, self.reasoning_trigger
            ]
        )
        
        # C. Game View Pipeline
        game_update_event = self.game_trigger.change(fn=lambda: None)
        self.game_view.receive_from(
            trigger_event=game_update_event,
            fn_fetch=lambda x: x,
            inputs=[self.game_buffer]
        )

        # D. Control UI Wiring
        if self.config.is_human:
            if isinstance(self.control_ui, SignalEmitter):
                self.control_ui.on_signal(fn=self._submit_user_input)
                   
        else:
            if isinstance(self.control_ui, AgentControlBaseUI):
                self.control_ui.on_signal(fn=self._handle_agent_command)
                
                reasoning_update_event = self.reasoning_trigger.change(fn=lambda: None)
                self.control_ui.receive_from(
                    trigger_event=reasoning_update_event,
                    fn_fetch=lambda x: x,
                    inputs=[self.reasoning_buffer]
                )

    def _submit_user_input(self, text: str) -> None:
        is_submited = self.manager.submit_user_input(text)
        if not is_submited:
            gr.Warning("Input could not be submitted")
        return 

    async def _kickstart_manager(self) -> gr.Timer:
        """
        Starts the asynchronous execution loop in the background.
        """
        asyncio.create_task(self.manager.start())
        return gr.Timer(active=False)

    async def _poll_everything(self):
        """
        Polls the manager for raw game events and agent reasoning tokens.
        Delegates rendering responsibility to the receiving UI components.
        """
        # Channel 1: Game Events (Raw Data Objects)
        game_out = (gr.skip(), gr.skip())
        updates = await self.manager.pop_pending_updates()
        if updates:
            game_out = (updates, str(uuid.uuid4()))

        # Channel 2: Reasoning (Tokens/Data)
        reasoning_out = (gr.skip(), gr.skip())
        if not self.config.is_human:
            tokens = await self.manager.pop_reasoning()
            if tokens:
                reasoning_out = (tokens, str(uuid.uuid4()))
        
        return (*game_out, *reasoning_out)

    def _handle_agent_command(self, command: AgentCommand):
        """
        Maps typed AgentCommands to manager flow control methods.
        """
        match command:
            case AgentCommand.PLAY:
                self.manager.play()
            case AgentCommand.PAUSE:
                self.manager.pause()
            case AgentCommand.STEP:
                self.manager.step()