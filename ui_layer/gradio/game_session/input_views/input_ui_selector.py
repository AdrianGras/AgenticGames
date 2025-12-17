from typing import Type, Any, Dict
from ui_layer.gradio.game_session.input_views.standard_input_view import StandardInputView
from ui_layer.gradio.signals import SignalEmitter

# Registry mapping game identifiers to their respective UI implementations.
# All registered classes must inherit from SignalEmitter to ensure 
# compatibility with the session orchestrator.
INPUT_UIs: Dict[str, Type[SignalEmitter]] = {
    "mistery_sequences": StandardInputView,
}

def get_input_ui(
    game_name: str, 
    **kwargs: Any
) -> SignalEmitter:
    """
    Factory function to instantiate the appropriate Input UI component.

    Args:
        game_name: The unique identifier of the game.
        **kwargs: Initialization arguments passed directly to the UI component 
                  constructor (e.g., game_name, theme, initial_state).

    Returns:
        SignalReceiver: An instance of a specialized Input UI component. 
                        Returns StandardInputView as a fallback if the game_name 
                        is not found in the registry.
    """
    # Fallback logic: if the game doesn't have a specialized UI, 
    # we use the basic text-box implementation.
    if game_name not in INPUT_UIs:
        return StandardInputView(**kwargs)
        
    ui_class = INPUT_UIs[game_name]
    return ui_class(**kwargs)