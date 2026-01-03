import os
import json
from datetime import datetime
from app_layer.execution.agent_evaluator import SessionResult, StatsReport

class EvaluationPersister:
    def __init__(self, game_name: str, agent_name: str, total_runs: int, base_dir: str = "outputs/evaluations"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_folder = f"run_{game_name}_{agent_name}_n{total_runs}_{timestamp}"
        
        self.output_path = os.path.join(base_dir, run_folder)
        self.sessions_path = os.path.join(self.output_path, "sessions")
        self.metrics_file = os.path.join(self.output_path, "metrics.jsonl")
        
        os.makedirs(self.sessions_path, exist_ok=True)

    def save_config(self, config_dict: dict):
        with open(os.path.join(self.output_path, "config.json"), "w", encoding="utf-8") as f:
            json.dump(config_dict, f, indent=4, ensure_ascii=False)

    def save_session(self, result: SessionResult):
        # Full metrics including turn-by-turn scores for variance analysis
        metric_line = {
            "session_id": result.session_id,
            "final_score": result.final_score,
            "is_failed": result.is_failed,
            "status": result.final_status,
            "total_turns": max(result.turn_history.keys(), default=0),
            "turn_history": result.turn_history  # Dict[turn, score]
        }
        with open(self.metrics_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(metric_line) + "\n")

        prefix = f"s{result.session_id:03d}"
        with open(os.path.join(self.sessions_path, f"{prefix}_reasoning.txt"), "w", encoding="utf-8") as f:
            f.write(result.reasoning_log)
            
        with open(os.path.join(self.sessions_path, f"{prefix}_history.txt"), "w", encoding="utf-8") as f:
            f.write(result.history_log)

    def save_final_report(self, report: StatsReport):
        data = {
            "total_runs": report.total_runs,
            "global_average_score": report.global_average_score,
            "total_failures": report.total_failures,
            "max_turns_reached": report.max_turns_reached,
            "average_score_per_turn": report.average_score_per_turn
        }
        with open(os.path.join(self.output_path, "final_report.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)