import asyncio
import sys
import shutil
import math
from tqdm import tqdm
from app_layer.execution.agent_evaluator import AgentEvaluator
from ui_layer.cli.cli_session_configurator import CLISessionConfigurator
from ui_layer.common.persistance import save_report_to_disk

def render_dashboard(active_sessions, completed, total):
    """Renders a multi-line grid of active sessions."""
    term_width = shutil.get_terminal_size().columns
    cell_width = 22 # Width of "[ID:000 T:000 S:000.0]"
    cols = max(1, term_width // cell_width)
    
    active = sorted([s for s in active_sessions if not s.is_finished], key=lambda x: x.session_id)
    
    lines = []
    lines.append(f"Progress: {completed}/{total} sessions completed")
    lines.append("-" * term_width)
    
    for i in range(0, len(active), cols):
        chunk = active[i:i+cols]
        row = " ".join([f"[ID:{s.session_id:02d} T:{s.current_turn:03d} S:{s.current_score:5.1f}]" for s in chunk])
        lines.append(row)
    
    return lines

async def main():
    number_of_samples = 10 
    configurator = CLISessionConfigurator()
    config = configurator.get_session_config()
    
    evaluator = AgentEvaluator(session_config=config, total_runs=number_of_samples)
    print(f"\033[?25l") # Hide cursor
    
    last_line_count = 0
    
    try:
        async for update in evaluator.run():
            # Clear previous lines
            if last_line_count > 0:
                sys.stdout.write(f"\033[{last_line_count}A") # Move up N lines
                for _ in range(last_line_count):
                    sys.stdout.write("\033[K\n") # Clear each line
                sys.stdout.write(f"\033[{last_line_count}A") # Move up again
            
            output_lines = render_dashboard(update.active_sessions, update.completed_count, update.total_runs)
            for line in output_lines:
                sys.stdout.write(line + "\n")
            
            last_line_count = len(output_lines)
            sys.stdout.flush()

    finally:
        sys.stdout.write("\033[?25h") # Show cursor

    report = evaluator.generate_report()
    print("\n=== Agent Evaluation Report ===")
    print(f"Global Average Score: {report.global_average_score:.2f}")
    print(f"Max Turns: {report.max_turns_reached}")
    
    save_path = save_report_to_disk(config, report, number_of_samples)
    print(f"Report saved: {save_path}")

if __name__ == "__main__":
    asyncio.run(main())