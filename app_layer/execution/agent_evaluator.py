import asyncio
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from typing import Dict, List, AsyncIterator, Optional
from collections import defaultdict
from dataclasses import dataclass

from app_layer.building.session_config import SessionConfig
from app_layer.execution.managers.direct_execution_manager import DirectExecutionManager
from app_layer.core.runner_types import GameStart, GameTurn, GameResult

@dataclass(frozen=True)
class SessionStatus:
    """Real-time status of a single evaluation session."""
    session_id: int
    current_turn: int
    current_score: float
    is_finished: bool = False

@dataclass(frozen=True)
class EvaluationUpdate:
    """Snapshot of the current evaluation state."""
    active_sessions: List[SessionStatus]
    completed_count: int
    total_runs: int

@dataclass(frozen=True)
class StatsReport:
    """Final aggregated results."""
    total_runs: int
    global_average_score: float
    average_score_per_turn: Dict[int, float]
    max_turns_reached: int

def _execute_session_task(session_id: int, config: SessionConfig, shared_state: Dict) -> tuple[Dict[int, float], float]:
    """Entry point for the worker process."""
    return asyncio.run(_run_logic(session_id, config, shared_state))

async def _run_logic(session_id: int, config: SessionConfig, shared_state: Dict) -> tuple[Dict[int, float], float]:
    """Async logic within the worker process."""
    history = {}
    final_score = 0.0
    manager = DirectExecutionManager(config)
    
    async for event in manager.execute():
        match event:
            case GameStart(initial_score=score):
                history[0] = score
                shared_state[session_id] = SessionStatus(session_id, 0, score)
            case GameTurn(iteration=it, score=score):
                history[it] = score
                shared_state[session_id] = SessionStatus(session_id, it, score)
            case GameResult(final_score=score):
                final_score = score
                shared_state[session_id] = SessionStatus(session_id, max(history.keys(), default=0), score, is_finished=True)
                
    return history, final_score

class AgentEvaluator:
    """Manages parallel execution and provides real-time progress updates."""

    def __init__(self, session_config: SessionConfig, total_runs: int = 100, max_workers: Optional[int] = None):
        self.session_config = session_config
        self.total_runs = total_runs
        self.max_workers = max_workers or multiprocessing.cpu_count()
        self.history: Dict[int, List[float]] = defaultdict(list)
        self.final_scores: List[float] = []

    async def run(self) -> AsyncIterator[EvaluationUpdate]:
        """Runs simulations and yields progress updates."""
        loop = asyncio.get_running_loop()
        manager = multiprocessing.Manager()
        shared_state = manager.dict()
        
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [
                loop.run_in_executor(executor, _execute_session_task, i, self.session_config, shared_state)
                for i in range(self.total_runs)
            ]
            
            pending = [asyncio.ensure_future(f) for f in futures]
            completed = 0
            
            while pending:
                # Wait for any task to finish or timeout to refresh UI
                done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED, timeout=0.5)
                
                for task in done:
                    session_history, final_score = await task
                    self._integrate_session(session_history, final_score)
                    completed += 1

                yield EvaluationUpdate(
                    active_sessions=list(shared_state.values()),
                    completed_count=completed,
                    total_runs=self.total_runs
                )

    def _integrate_session(self, session_history: Dict[int, float], final_score: float):
        self.final_scores.append(final_score)
        for turn, score in session_history.items():
            self.history[turn].append(score)

    def generate_report(self) -> StatsReport:
        """Computes final statistics from collected data."""
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