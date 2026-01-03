import asyncio
import multiprocessing
import copy
from concurrent.futures import ProcessPoolExecutor
from typing import Dict, List, AsyncIterator, Optional, Any
from collections import defaultdict
from dataclasses import dataclass, asdict

from app_layer.building.session_config import SessionConfig
from app_layer.execution.managers.direct_execution_manager import DirectExecutionManager
from app_layer.core.runner_types import GameStart, GameTurn, GameResult, GameStatus

@dataclass(frozen=True)
class SessionStatus:
    session_id: int
    current_turn: int
    current_score: float
    is_finished: bool = False
    is_failed: bool = False

@dataclass(frozen=True)
class SessionResult:
    session_id: int
    final_score: float
    turn_history: Dict[int, float]
    history_log: str
    reasoning_log: str
    final_status: str
    is_failed: bool

@dataclass(frozen=True)
class EvaluationUpdate:
    active_sessions: List[SessionStatus]
    completed_count: int
    total_runs: int
    last_session_result: Optional[SessionResult] = None

@dataclass(frozen=True)
class StatsReport:
    total_runs: int
    global_average_score: float
    average_score_per_turn: Dict[int, float]
    max_turns_reached: int
    total_failures: int
    config_snapshot: Dict[str, Any]

def _execute_session_task(session_id: int, config: SessionConfig, shared_state: Dict) -> SessionResult:
    return asyncio.run(_run_logic(session_id, config, shared_state))

async def _run_logic(session_id: int, config: SessionConfig, shared_state: Dict) -> SessionResult:
    history = {}
    reasonings = []
    final_score = 0.0
    history_log = ""
    res_status = "UNKNOWN"
    is_failed = False
    
    async def capture_reasoning(data: Any):
        reasonings.append(str(data))
    
    config.agent_params["on_reasoning"] = capture_reasoning
    manager = DirectExecutionManager(config)

    async for event in manager.execute():
        match event:
            case GameStart(initial_score=score):
                history[0] = score
                shared_state[session_id] = SessionStatus(session_id, 0, score)
            case GameTurn(iteration=it, score=score):
                history[it] = score
                shared_state[session_id] = SessionStatus(session_id, it, score)
            case GameResult(final_score=score, history_log=log, final_status=final_status):
                final_score = score
                history_log = log
                res_status = str(final_status)
                is_failed = final_status == GameStatus.FAILED
                
                shared_state[session_id] = SessionStatus(
                    session_id=session_id, 
                    current_turn=max(history.keys(), default=0), 
                    current_score=score, 
                    is_finished=True,
                    is_failed=is_failed
                )
                
    return SessionResult(
        session_id=session_id,
        final_score=final_score,
        turn_history=history,
        history_log=history_log,
        reasoning_log="".join(reasonings),
        final_status=res_status,
        is_failed=is_failed
    )

class AgentEvaluator:
    def __init__(self, session_config: SessionConfig, total_runs: int = 100, max_workers: Optional[int] = None):
        self.session_config = session_config
        self.total_runs = total_runs
        self.max_workers = max_workers or multiprocessing.cpu_count()
        self.history: Dict[int, List[float]] = defaultdict(list)
        self.final_scores: List[float] = []
        self.failure_count = 0

    async def run(self) -> AsyncIterator[EvaluationUpdate]:
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
                done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED, timeout=0.5)
                
                for task in done:
                    result: SessionResult = await task
                    self._integrate_session(result)
                    completed += 1
                    yield EvaluationUpdate(list(shared_state.values()), completed, self.total_runs, result)
                
                if not done:
                    yield EvaluationUpdate(list(shared_state.values()), completed, self.total_runs)

    def _integrate_session(self, result: SessionResult):
        self.final_scores.append(result.final_score)
        if result.is_failed:
            self.failure_count += 1
        for turn, score in result.turn_history.items():
            self.history[turn].append(score)

    def generate_report(self) -> StatsReport:
        avg_per_turn = {t: sum(s)/len(s) for t, s in sorted(self.history.items())}
        clean_config = copy.deepcopy(self.session_config)
        if clean_config.agent_params and "on_reasoning" in clean_config.agent_params:
            del clean_config.agent_params["on_reasoning"]

        return StatsReport(
            total_runs=len(self.final_scores),
            global_average_score=sum(self.final_scores)/len(self.final_scores) if self.final_scores else 0.0,
            average_score_per_turn=avg_per_turn,
            max_turns_reached=max(avg_per_turn.keys(), default=0),
            total_failures=self.failure_count,
            config_snapshot=asdict(clean_config)
        )