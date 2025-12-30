from typing import Type, Any, Dict
from ui_layer.gradio.game_session.game_views.standard_game_view import StandardGameView
from ui_layer.gradio.signals import SignalReceiver

# Registry mapping game identifiers to their respective UI implementations.
# All registered classes must inherit from SignalReceiver to ensure 
# compatibility with the session orchestrator.
GAME_UIs: Dict[str, Type[SignalReceiver]] = {
    "mystery_sequences": StandardGameView,
}

def get_game_ui(
    game_name: str, 
    **kwargs: Any
) -> SignalReceiver:
    """
    Factory function to instantiate the appropriate Game UI component.

    Args:
        game_name: The unique identifier of the game.
        **kwargs: Initialization arguments passed directly to the UI component 
                  constructor (e.g., game_name, theme, initial_state).

    Returns:
        SignalReceiver: An instance of a specialized Game UI component. 
                        Returns StandardGameView as a fallback if the game_name 
                        is not found in the registry.
    """
    # Fallback logic: if the game doesn't have a specialized UI, 
    # we use the basic text-based implementation.
    if game_name not in GAME_UIs:
        return StandardGameView(game_name,**kwargs)
        
    ui_class = GAME_UIs[game_name]
    return ui_class(game_name, **kwargs)