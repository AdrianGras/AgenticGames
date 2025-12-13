from game_layer.games.game_selector import list_available_games, get_game
from agent_layer.agents.agent_selector import list_available_agents, get_agent
from agent_layer.LLMs.llm_selector import list_available_llms, get_llm
import gradio as gr
from enum import Enum, auto
from game_layer.game_engine.core_engine import GameStatus


class AppMode(Enum):
    USER = auto()
    AGENT = auto()


class GameApp:
    def __init__(self):
        self.game = None
        self.agent = None
        self.mode = AppMode.USER

        self.is_stop_requested = False
        self.is_agent_running = False

        self.game_ui = None
        self.agent_ui = None
        self.input_interface_ui = None

    # -------------- UI Builders -----------------

    def build_game_selector(self):
        return gr.Dropdown(
            choices=list_available_games(),
            label="Select a Game",
            interactive=True,
        )

    def build_mode_selector(self):
        return gr.Radio(
            choices=[
                ("User", AppMode.USER.value),
                ("Agent", AppMode.AGENT.value),
            ],
            label="Mode",
            value=AppMode.USER.value,
            interactive=True,
        )

    def build_agent_selector(self):
        return gr.Dropdown(
            choices=list_available_agents(),
            label="Select Agent",
            interactive=True,
            visible=False,
        )

    def build_llm_selector(self):
        return gr.Dropdown(
            choices=list_available_llms(),
            label="Select LLM",
            interactive=True,
            visible=False,
        )

    def build_start_button(self):
        return gr.Button("Start Game")

    def build_agent_controls(self):
        with gr.Row(visible=False) as self.agent_controls_panel:
            agent_start_btn = gr.Button("Start", visible=True)
            agent_stop_btn = gr.Button("Stop", visible=False)
            agent_continue_btn = gr.Button("Continue", visible=False)
        return agent_start_btn, agent_stop_btn, agent_continue_btn

    # -------------- BUILD FULL UI -----------------

    def build_app_ui(self):
        """
        Build the entire UI layout and return the gr.Blocks object.
        """
        with gr.Blocks() as demo:
            # --- SETUP PANEL ---
            with gr.Column() as self.setup_panel:
                gr.Markdown("## Game Setup")

                self.game_selector = self.build_game_selector()
                self.mode_selector = self.build_mode_selector()
                self.agent_selector = self.build_agent_selector()
                self.llm_selector = self.build_llm_selector()
                self.start_button = self.build_start_button()

                self.mode_selector.change(
                    fn=self.on_mode_changed,
                    inputs=[self.mode_selector],
                    outputs=[self.agent_selector, self.llm_selector],
                )

            # --- GAME PANEL ---
            with gr.Row(visible=False) as self.game_panel:
                with gr.Column() as self.game_state_column:
                    self.game_ui = build_game_ui(self.game_state_column)

                with gr.Column() as self.interaction_column:
                    self.agent_start_btn, self.agent_stop_btn, self.agent_continue_btn = self.build_agent_controls()

                    self.agent_ui = build_agent_interface()
                    self.input_interface_ui = build_user_input_interface()

            # ---- Output wiring helpers ----
            game_outputs = list(self.game_ui.get_components())
            agent_outputs = list(self.agent_ui.get_components())
            user_outputs = list(self.input_interface_ui.get_components())

            agent_control_outputs = [
                self.agent_controls_panel,
                self.agent_start_btn,
                self.agent_stop_btn,
                self.agent_continue_btn,
            ]

            start_game_outputs = [
                self.setup_panel,
                self.game_panel,
                *agent_control_outputs,
                *agent_outputs,
                *user_outputs,
                *game_outputs,
            ]

            agent_control_only_outputs = [*agent_control_outputs]

            agent_stream_outputs = [
                *agent_control_outputs,
                *agent_outputs,
                *game_outputs,
            ]

            # --- Start Game ---
            self.start_button.click(
                fn=self.on_start_clicked,
                inputs=[
                    self.game_selector,
                    self.mode_selector,
                    self.agent_selector,
                    self.llm_selector,
                ],
                outputs=start_game_outputs,
            )

            # --- USER submit wiring (Option A) ---
            # input_interface_ui owns its .click(...) internally; we only chain a .then(...)
            # that consumes the emitted action and updates the game UI.
            self.input_interface_ui.get_submit_event().then(
                fn=self.user_action_handler,
                inputs=[self.input_interface_ui.get_action_output()],
                outputs=game_outputs,
                show_progress=False,
            )

            # --- Agent Start (toggle buttons, then stream loop) ---
            start_evt = self.agent_start_btn.click(
                fn=self.on_agent_start_clicked,
                inputs=[],
                outputs=agent_control_only_outputs,
            )
            start_evt.then(
                fn=self.run_agent_loop,
                inputs=[],
                outputs=agent_stream_outputs,
                show_progress=False,
            )

            # --- Agent Stop ---
            self.agent_stop_btn.click(
                fn=self.on_agent_stop_clicked,
                inputs=[],
                outputs=agent_control_only_outputs,
            )

            # --- Agent Continue (toggle buttons, then stream loop) ---
            cont_evt = self.agent_continue_btn.click(
                fn=self.on_agent_continue_clicked,
                inputs=[],
                outputs=agent_control_only_outputs,
            )
            cont_evt.then(
                fn=self.run_agent_loop,
                inputs=[],
                outputs=agent_stream_outputs,
                show_progress=False,
            )

        return demo

    # ------------------------------------------------
    # CALLBACKS
    # ------------------------------------------------

    def on_mode_changed(self, mode_int):
        """
        Show/hide Agent + LLM selectors based on the selected mode.
        """
        mode = AppMode(mode_int)
        if mode == AppMode.AGENT:
            return (gr.update(visible=True), gr.update(visible=True))
        return (gr.update(visible=False), gr.update(visible=False))

    def game_finished_handler(self):
        """
        Hook for when the game finishes.
        """
        pass

    def game_failed_handler(self):
        """
        Hook for when the game fails.
        """
        pass

    def user_action_handler(self, action):
        """
        Apply a user action to the game and return updates for game_ui components.

        The input UI emits the action via an internal "bridge" component; this method
        consumes that action and returns `*game_ui.render()` (Option A).
        """
        if self.game is None:
            return self.game_ui.render()

        observation = self.game.step(action)
        self.game_ui.set_observation(observation)

        current_status = self.game.get_game_status()
        if current_status == GameStatus.FAILED:
            self.game_failed_handler()
        elif current_status == GameStatus.FINISHED:
            self.game_finished_handler()

        return self.game_ui.render()

    def on_start_clicked(self, game_name, mode_int, agent_name, llm_name):
        """
        Instantiate the selected game and the selected interaction mode.

        This callback prepares the UI but does not auto-run anything.
        """
        self.is_stop_requested = False
        self.is_agent_running = False

        self.game = get_game(game_name)
        self.mode = AppMode(mode_int)

        initial_observation = self.game.get_initial_observation()

        self.game_ui.reset(game_name=game_name, game=self.game)
        self.game_ui.set_observation(initial_observation)

        if self.mode == AppMode.AGENT:
            llm = get_llm(llm_name)
            self.agent = get_agent(agent_name, llm)

            self.agent_ui.reset(agent_name=agent_name, agent=self.agent)
            self.agent_ui.clear()

            self.input_interface_ui.hide()

            agent_controls_visible = True
            agent_start_visible = True
            agent_stop_visible = False
            agent_continue_visible = False
        else:
            self.agent = None

            self.agent_ui.clear()
            self.input_interface_ui.reset(game_name=game_name)
            self.input_interface_ui.show()

            agent_controls_visible = False
            agent_start_visible = False
            agent_stop_visible = False
            agent_continue_visible = False

        return (
            gr.update(visible=False),  # setup_panel
            gr.update(visible=True),   # game_panel
            gr.update(visible=agent_controls_visible),  # agent_controls_panel
            gr.update(visible=agent_start_visible),     # agent_start_btn
            gr.update(visible=agent_stop_visible),      # agent_stop_btn
            gr.update(visible=agent_continue_visible),  # agent_continue_btn
            *self.agent_ui.render(),
            *self.input_interface_ui.render(),
            *self.game_ui.render(),
        )

    def on_agent_start_clicked(self):
        """
        Switch controls to RUNNING state and prepare the agent loop.
        """
        if self.mode != AppMode.AGENT or self.game is None or self.agent is None:
            return (gr.update(), gr.update(), gr.update(), gr.update())

        self.is_stop_requested = False
        self.is_agent_running = True

        return (
            gr.update(visible=True),   # agent_controls_panel
            gr.update(visible=False),  # start
            gr.update(visible=True),   # stop
            gr.update(visible=False),  # continue
        )

    def on_agent_stop_clicked(self):
        """
        Request the running agent loop to stop and switch controls to PAUSED state.
        """
        self.is_stop_requested = True
        self.is_agent_running = False

        return (
            gr.update(visible=True),   # agent_controls_panel
            gr.update(visible=False),  # start
            gr.update(visible=False),  # stop
            gr.update(visible=True),   # continue
        )

    def on_agent_continue_clicked(self):
        """
        Switch controls back to RUNNING state and resume the agent loop.
        """
        if self.mode != AppMode.AGENT or self.game is None or self.agent is None:
            return (gr.update(), gr.update(), gr.update(), gr.update())

        self.is_stop_requested = False
        self.is_agent_running = True

        return (
            gr.update(visible=True),   # agent_controls_panel
            gr.update(visible=False),  # start
            gr.update(visible=True),   # stop
            gr.update(visible=False),  # continue
        )

    def run_agent_loop(self):
        """
        Stream agent reasoning tokens and game updates until stopped or terminal state.

        Yields:
            Updates for (agent_controls_panel, start_btn, stop_btn, continue_btn)
            + agent_ui components + game_ui components.
        """
        if self.mode != AppMode.AGENT or self.game is None or self.agent is None:
            yield (
                gr.update(), gr.update(), gr.update(), gr.update(),
                *self.agent_ui.render(),
                *self.game_ui.render(),
            )
            return

        while self.game.get_game_status() == GameStatus.RUNNING:
            if self.is_stop_requested:
                break

            observation = self.game_ui.get_observation()
            internal_reasoning, action_fut = self.agent.get_future_action(observation)

            for token in internal_reasoning:
                if self.is_stop_requested:
                    break
                self.agent_ui.push_token(token)
                yield (
                    gr.update(), gr.update(), gr.update(), gr.update(),
                    *self.agent_ui.render(),
                    *self.game_ui.render(),
                )

            if self.is_stop_requested:
                break

            try:
                action = action_fut.result()
            except Exception as e:
                self.agent_ui.push_error(f"Agent error: {e}")
                self.game_failed_handler()
                yield (
                    gr.update(), gr.update(), gr.update(), gr.update(),
                    *self.agent_ui.render(),
                    *self.game_ui.render(),
                )
                return

            observation = self.game.step(action)
            self.game_ui.set_observation(observation)

            yield (
                gr.update(), gr.update(), gr.update(), gr.update(),
                *self.agent_ui.render(),
                *self.game_ui.render(),
            )

            status = self.game.get_game_status()
            if status == GameStatus.FINISHED:
                self.game_finished_handler()
                break
            if status == GameStatus.FAILED:
                self.game_failed_handler()
                break

        if self.is_stop_requested and self.game.get_game_status() == GameStatus.RUNNING:
            yield (
                gr.update(visible=True),   # agent_controls_panel
                gr.update(visible=False),  # start
                gr.update(visible=False),  # stop
                gr.update(visible=True),   # continue
                *self.agent_ui.render(),
                *self.game_ui.render(),
            )
            return

        yield (
            gr.update(visible=True),   # agent_controls_panel
            gr.update(visible=True),   # start
            gr.update(visible=False),  # stop
            gr.update(visible=False),  # continue
            *self.agent_ui.render(),
            *self.game_ui.render(),
        )


"""
Required interface for UI wrappers (to implement in your factories):

build_game_ui(column) -> game_ui
- get_components() -> list[gr.Component]
- reset(game_name: str, game: object) -> None
- set_observation(obs: object) -> None
- get_observation() -> object
- render() -> tuple|list  (same length/order as get_components)

build_agent_interface(...) -> agent_ui
- get_components() -> list[gr.Component]
- reset(agent_name: str, agent: object) -> None
- clear() -> None
- push_token(token: str) -> None
- push_error(msg: str) -> None
- render() -> tuple|list  (same length/order as get_components)

build_user_input_interface(...) -> input_interface_ui
- get_components() -> list[gr.Component]
- reset(game_name: str) -> None
- show() -> None
- hide() -> None
- render() -> tuple|list  (same length/order as get_components)

- get_submit_event() -> gradio.events.Dependency
    Returns the Dependency created by submit_btn.click(...).

- get_action_output() -> gr.Component
    Returns a "bridge" component (commonly a hidden Textbox) that holds the submitted action
    so GameApp can chain `.then(...)` with it as input.

Behavioral requirement:
- input_interface_ui must register its own submit_btn.click(...) internally, and must write
  the submitted action into get_action_output() as an output of that click.
"""
