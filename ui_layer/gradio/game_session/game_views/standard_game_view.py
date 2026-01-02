import gradio as gr
from typing import List, Any, Dict
from ui_layer.gradio.signals import SignalReceiver
from app_layer.core.runner_types import GameEvent, GameStart, GameTurn, GameResult
from game_layer.game_engine.core_engine import GameStatus

class StandardGameView(SignalReceiver):
    """
    Renders the game flow as a conversational interaction:
    - User role: Represents Agent Actions (Right side).
    - Assistant role: Represents Game Observations and System Messages (Left side).
    
    This view uses the Chatbot component to leverage native autoscroll 
    and clear visual separation between player moves and environment feedback.
    """

    def __init__(self, game_name: str):
        """
        Initializes the game view with a Chatbot display and an empty message buffer.

        Args:
            game_name (str): The display name of the current game.
        """
        self._history_buffer: List[Dict[str, str]] = []
        
        with gr.Group():
            with gr.Row():
                gr.Markdown(f"### 🎮 Playing: {game_name}")
                self.score_display = gr.Number(
                    label="Current Score", 
                    value=0.0,
                    interactive=False,
                    precision=2
                )
            
            self.display_area = gr.Chatbot(
                value=[],
                type="messages",
                label="Game Interaction",
                show_label=False,
                height=600,
                show_copy_button=True,
                bubble_full_width=False,
                render_markdown=True
            )

        super().__init__(targets=[self.display_area, self.score_display])

    def update(self, events: List[GameEvent]) -> Any:
        """
        Processes new domain events and updates the chatbot history.

        Args:
            events (List[GameEvent]): New events emitted by the game engine.

        Returns:
            List[Dict[str, str]]: The updated message history for Gradio rendering.
        """
        if not events:
            return gr.skip()

        for event in events:
            new_messages = self._event_to_messages(event)
            self._history_buffer.extend(new_messages)

        last_event = events[-1]
        score = self._get_score(last_event)

        return self._history_buffer, score

    def _event_to_messages(self, event: GameEvent) -> List[Dict[str, str]]:
        """
        Translates Domain Events into a list of Chatbot messages.
        
        Maps actions to 'user' role and observations to 'assistant' role.
        """
        match event:
            case GameStart(initial_observation=obs):
                return [{
                    "role": "assistant",
                    "content": f"### 🏁 Game Start\n\n{obs}"
                }]

            case GameTurn(iteration=i, observation=obs, action=act):
                return [
                    {
                        "role": "user",
                        "content": act
                    },
                    {
                        "role": "assistant",
                        "content": obs
                    }
                ]

            case GameResult(final_status=status):
                header = "## 🏆 MISSION ACCOMPLISHED" if status == GameStatus.FINISHED else "## 💀 GAME OVER"
                return [{
                    "role": "assistant",
                    "content": header
                }]

            case _:
                return [{
                    "role": "assistant",
                    "content": f"**System Event:** {str(event)}"
                }]
            
    def _get_score(self, event: GameEvent) -> float:
        """
        Extracts the score from the given event if available.

        Args:
            event (GameEvent): The event to extract the score from.

        Returns:
            float: The extracted score, or 0.0 if not applicable.
        """
        match event:
            case GameTurn(score=score):
                return score
            case GameResult(final_score=score):
                return score
            case GameStart(initial_score=score):
                return score
            case _:
                return 0.0