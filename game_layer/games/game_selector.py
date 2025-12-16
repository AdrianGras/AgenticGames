from typing import List, Type, Any
from game_layer.game_engine.core_engine import CoreEngine
from game_layer.games.level_based_games.mistery_secuences.mistery_secuences import MisterySecuences

GAMES: dict[str, Type[CoreEngine]] = {
    "mistery_sequences": MisterySecuences,
}

def get_game(game_name: str, **kwargs: Any) -> CoreEngine:
    """
    Factory function to instantiate a Game Engine.

    Args:
        game_name (str): The identifier of the game logic.
        **kwargs: Additional configuration parameters for the game's constructor 
                  (e.g., difficulty, seed, max_levels).

    Returns:
        CoreEngine: An instantiated game ready for the session.

    Raises:
        ValueError: If the game_name is not registered.
    """
    if game_name not in GAMES:
        raise ValueError(
            f"Game '{game_name}' not found. "
            f"Available games: {list_available_games()}"
        )

    game_class = GAMES[game_name]

    return game_class(**kwargs)

def list_available_games() -> List[str]:
    """
    Returns a list of all supported game identifiers.
    """
    return list(GAMES.keys())