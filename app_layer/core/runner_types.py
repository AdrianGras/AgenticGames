from dataclasses import dataclass
from game_layer.game_engine.core_engine import GameStatus
from typing import Union

@dataclass
class GameStart:
    """
    Represents the initial state of the game session before the loop begins.
    
    Attributes:
        initial_observation (str): The opening text or scene description provided by the game.
        game_name (str): The identifier of the game being played.
    """
    initial_observation: str
    game_name: str
    initial_score: float

@dataclass
class GameTurn:
    """
    Represents a single completed step in the game loop.
    
    This object is yielded after the actor has performed an action and the 
    game engine has processed it.
    
    Attributes:
        iteration (int): The current turn number (1-based index).
        action (str): The specific command issued by the actor.
        observation (str): The outcome of the action.
    """
    iteration: int
    action: str
    observation: str
    score: float

@dataclass
class GameResult:
    """
    Represents the final outcome of the game session.
    
    This object is yielded exactly once when the game loop terminates.
    
    Attributes:
        final_status (GameStatus): The ending state (FINISHED or FAILED).
        history_log (str): The complete textual record of all inputs and observations.
    """
    final_status: GameStatus
    final_score: float
    history_log: str

GameEvent = Union[GameStart, GameTurn, GameResult]
