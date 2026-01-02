import json
from pathlib import Path
from dataclasses import asdict
from datetime import datetime
from app_layer.execution.agent_evaluator import StatsReport
from app_layer.building.session_config import SessionConfig

def save_report_to_disk(config: SessionConfig, report: StatsReport, number_of_samples, base_path="outputs/reports"):
    """
    Utility to persist a report. 
    """
    path = Path(base_path)
    path.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"eval_{config.game_name}_{config.agent_name}_n{number_of_samples}_{timestamp}.json"
    
    data_to_save = {
        "config": asdict(config),
        "results": asdict(report),
        "number_of_samples": number_of_samples
    }
    
    full_path = path / filename
    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(data_to_save, f, indent=4)
    
    return full_path