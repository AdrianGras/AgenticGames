import asyncio
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from typing import Dict, List, Any, Optional
from collections import defaultdict
from dataclasses import dataclass, field
from tqdm import tqdm

from app_layer.session_builder import AgentSessionBuilder
from app_layer.session_config import SessionConfig
from app_layer.runner_types import GameStart, GameTurn, GameResult

@dataclass(frozen=True)
class StatsReport:
    """
    Immutable structured report containing the aggregated results 
    of the simulation runs.
    """
    total_runs: int
    global_average_score: float
    average_score_per_turn: Dict[int, float]
    max_turns_reached: int

def _execute_session_task(config: SessionConfig) -> tuple[Dict[int, float], float]:
    """
    Worker task executing a single game session. 
    Returns the session history and final score.
    """
    return asyncio.run(_run_logic(config))

async def _run_logic(config: SessionConfig) -> tuple[Dict[int, float], float]:
    """
    Internal async logic for a single session.
    """
    history = {}
    final_score = 0.0
    
    builder = AgentSessionBuilder(
        game_name=config.game_name,
        agent_name=config.agent_name,
        game_params=config.game_params,
        agent_params=config.agent_params
    )
    runner = builder.build()
    
    async for event in runner.run():
        match event:
            case GameStart(initial_score=score):
                history[0] = score
            case GameTurn(iteration=it, score=score):
                history[it] = score
            case GameResult(final_score=score):
                final_score = score
                
    return history, final_score

class StatsRunner:
    """
    A dynamic Work Pool runner that executes game sessions across multiple 
    processes with structured output and real-time feedback.
    """

    def __init__(self, session_config: SessionConfig, total_runs: int = 100, max_workers: int = None):
        self.session_config = session_config
        self.total_runs = total_runs
        # Optimized for I/O bound tasks
        self.max_workers = max_workers or (multiprocessing.cpu_count() * 5)
        
        self.history: Dict[int, List[float]] = defaultdict(list)
        self.final_scores: List[float] = []

    async def run(self) -> StatsReport:
        """
        Executes simulations and returns a structured StatsReport.
        """
        loop = asyncio.get_running_loop()
        progress_bar = tqdm(total=self.total_runs, desc="Simulating", unit="game")

        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_run = [
                loop.run_in_executor(executor, _execute_session_task, self.session_config)
                for _ in range(self.total_runs)
            ]
            
            for future in asyncio.as_completed(future_to_run):
                session_history, final_score = await future
                self._integrate_session(session_history, final_score)
                progress_bar.update(1)

        progress_bar.close()
        return self._generate_report()

    def _integrate_session(self, session_history: Dict[int, float], final_score: float):
        """Integrates a single session's data into the global state."""
        self.final_scores.append(final_score)
        for turn, score in session_history.items():
            self.history[turn].append(score)

    def _generate_report(self) -> StatsReport:
        """Computes averages and returns a StatsReport object."""
        avg_per_turn = {
            turn: sum(scores) / len(scores) 
            for turn, scores in sorted(self.history.items())
        }
        
        global_avg = sum(self.final_scores) / len(self.final_scores) if self.final_scores else 0.0
        max_turns = max(avg_per_turn.keys()) if avg_per_turn else 0

        return StatsReport(
            total_runs=len(self.final_scores),
            global_average_score=global_avg,
            average_score_per_turn=avg_per_turn,
            max_turns_reached=max_turns
        )