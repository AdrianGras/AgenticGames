from typing import AsyncGenerator, Union
from game_layer.game_engine.core_engine import CoreEngine, GameStatus
from agent_layer.actor import Actor
from app_layer.runner_types import GameEvent, GameStart, GameTurn, GameResult

class GameRunner:
    """
    Orchestrates the asynchronous interaction between the Game Engine and the Actor.
    
    This class implements an asynchronous generator pattern. Instead of running 
    a closed loop, it yields structured data (Start, Turn, Result) to the caller 
    step-by-step. This allows the controlling layer (Main CLI or UI) to manage 
    flow control, rate limiting, and presentation logic independently.
    """

    def __init__(self, game: CoreEngine, actor: Actor):
        """
        Initialize the Game Runner.

        Args:
            game (CoreEngine): The synchronous game engine instance, responsible for 
                               state management and logic.
            actor (Actor): The asynchronous entity (AI Agent or Human Adapter) 
                           responsible for making decisions.
        """
        self.game = game
        self.actor = actor

    async def run(self) -> AsyncGenerator[GameEvent, None]:
        """
        Executes the main game loop indefinitely until the Game Engine signals a stop.

        The method handles the flow in three phases:
        1. **Initialization**: Starts the game and yields the initial scene.
        2. **Loop**: Alternates between Actor decisions and Game steps. 
           Input validation errors are handled internally by the Game Engine 
           and returned as standard observations.
        3. **Termination**: Determines the final result based on the Game Status.

        Yields:
            GameStart: Once, upon initialization.
            GameTurn: Repeatedly, for every action taken.
            GameResult: Once, when the game status is no longer RUNNING.
        """
        # 1. Initialization Phase
        current_observation = self.game.start()
        score = self.game.get_score()
        yield GameStart(
            initial_observation=current_observation,
            game_name=self.game.name,
            initial_score=score
        )

        iteration = 0
        
        # 2. Main Loop Phase
        while self.game.game_status == GameStatus.RUNNING:
            
            action = await self.actor.get_action(current_observation)

            new_observation = self.game.step(action)
            score = self.game.get_score()
            yield GameTurn(
                iteration=iteration + 1,
                action=action,
                observation=new_observation,
                score=score
            )

            current_observation = new_observation
            iteration += 1

        # 3. Termination Phase
        final_score = self.game.get_score()
        yield GameResult(
            final_status=self.game.game_status,
            history_log=self.game.get_full_history(),
            final_score=final_score
        )