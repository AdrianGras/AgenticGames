import gradio as gr
from typing import List, Any
from ui_layer.gradio.signals import SignalReceiver
from app_layer.runner_types import GameEvent, GameStart, GameTurn, GameResult
from game_layer.game_engine.core_engine import GameStatus

class StandardGameView(SignalReceiver):
    """
    A rich-text game output component that renders game events using Markdown.
    
    Features:
    - Renders styling (bold, code blocks, quotes) for better readability.
    - Accumulates history in an internal buffer.
    - Handles polymorphic GameEvent objects directly.
    """

    def __init__(self, game_name: str):
        """
        Initializes the view with a Markdown component and an empty history buffer.

        Args:
            game_name: The title of the game for the header.
        """
        self._history_buffer: List[str] = []
        
        with gr.Group():
            gr.Markdown(f"### 🎮 Playing: {game_name}")
            
            # We use a Markdown component for rich text rendering (bold, code, etc.)
            self.display_area = gr.Markdown(
                value="*Waiting for game start...*",
                elem_classes=["game-log-container"], # Useful for custom CSS if needed
                height=500, # Fixed height with internal scroll is better for logs
            )

        # Initialize SignalReceiver with the target component
        super().__init__(targets=[self.display_area])

    def update(self, events: List[GameEvent]) -> Any:
        """
        Receives raw domain events, converts them to Markdown, and updates the view.
        
        Args:
            events: A list of GameStart, GameTurn, or GameResult objects.
            
        Returns:
            str: The full rendered Markdown history.
        """
        if not events:
            return gr.skip()

        # Process new events and append to history
        for event in events:
            rendered_chunk = self._render_event(event)
            self._history_buffer.append(rendered_chunk)

        # Join all history chunks into a single Markdown document
        full_log = "\n\n".join(self._history_buffer)
        
        return full_log

    def _render_event(self, event: GameEvent) -> str:
        """
        Presentation Logic: Converts Domain Objects into styled Markdown strings.
        """
        match event:
            case GameStart(initial_observation=obs):
                return (
                    f"---\n"
                    f"{obs}\n"
                    f"---"
                )

            case GameTurn(iteration=i, observation=obs, action=act):
                return (
                    f"**Action:** `{act}`\n\n"
                    f"> {obs}\n"

                )

            case GameResult(final_status=status):
                if status == GameStatus.FINISHED:
                    header = "## 🏆 MISSION ACCOMPLISHED"
                else:
                    header = "## 💀 GAME OVER"
                
                return f"\n---\n{header}\n---"

            case _:
                return f"**Unknown Event:** {str(event)}"