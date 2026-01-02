import asyncio
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from typing import Dict, List, Any, Optional
from collections import defaultdict
from dataclasses import dataclass
from tqdm import tqdm

from app_layer.session_config import SessionConfig
from app_layer.direct_execution_manager import DirectExecutionManager
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
    Worker task executing a single game session via DirectExecutionManager.
    """
    return asyncio.run(_run_logic(config))

async def _run_logic(config: SessionConfig) -> tuple[Dict[int, float], float]:
    """
    Internal async logic consuming the DirectExecutionManager stream.
    """
    history = {}
    final_score = 0.0
    
    manager = DirectExecutionManager(config)
    
    async for event in manager.execute():
        match event:
            case GameStart(initial_score=score):
                history[0] = score
            case GameTurn(iteration=it, score=score):
                history[it] = score
            case GameResult(final_score=score):
                final_score = score
                
    return history, final_score

class AgentEvaluator:
    """
    Manages the execution of multiple game sessions for statistical evaluation.
    """

    def __init__(self, session_config: SessionConfig, total_runs: int = 100, max_workers: int = None):
        if session_config.is_human:
            raise ValueError("StatsRunner: Human sessions are not supported for statistics gathering.")

        self.session_config = session_config
        self.total_runs = total_runs
        self.max_workers = max_workers or (multiprocessing.cpu_count() * 2)
        
        self.history: Dict[int, List[float]] = defaultdict(list)
        self.final_scores: List[float] = []

    async def run(self) -> StatsReport:
        """
        Executes simulations across processes and aggregates results.
        """
        loop = asyncio.get_running_loop()
        progress_bar = tqdm(total=self.total_runs, desc="Simulating", unit="game")

        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:            
            tasks = [
                loop.run_in_executor(executor, _execute_session_task, self.session_config)
                for _ in range(self.total_runs)
            ]
            
            for future in asyncio.as_completed(tasks):
                session_history, final_score = await future
                self._integrate_session(session_history, final_score)
                progress_bar.update(1)

        progress_bar.close()
        return self._generate_report()

    def _integrate_session(self, session_history: Dict[int, float], final_score: float):
        self.final_scores.append(final_score)
        for turn, score in session_history.items():
            self.history[turn].append(score)

    def _generate_report(self) -> StatsReport:
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