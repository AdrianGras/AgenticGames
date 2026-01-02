from app_layer.execution.agent_evaluator import AgentEvaluator
from ui_layer.cli.cli_session_configurator import CLISessionConfigurator
from ui_layer.common.persistance import save_report_to_disk


async def main():

    number_of_samples = 50
    configurator = CLISessionConfigurator()
    config = configurator.get_session_config()
    evaluator = AgentEvaluator(session_config=config, total_runs=number_of_samples)
    
    report = await evaluator.run()
    
    print("=== Agent Evaluation Report ===")
    print(f"Total Runs: {report.total_runs}")
    print(f"Global Average Score: {report.global_average_score:.2f}")
    print(f"Max Turns Reached: {report.max_turns_reached}")
    print("Average Score Per Turn:")
    for turn, avg_score in report.average_score_per_turn.items():
        print(f"  Turn {turn}: {avg_score:.2f}")
    save_path = save_report_to_disk(config, report, number_of_samples)
    print(f"Report saved to: {save_path}")

