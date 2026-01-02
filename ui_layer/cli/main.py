
import os
import asyncio
import sys
from ui_layer.cli.cli_session_configurator import CLISessionConfigurator
from app_layer.execution.managers.direct_execution_manager import DirectExecutionManager
from app_layer.core.runner_types import GameEvent, GameStart, GameTurn, GameResult
from app_layer.io.input_source import InputSource




class StandardInputSource(InputSource):
    async def get(self) -> str:
        return await asyncio.to_thread(input, "\n>> Enter action: ")
    
async def cli_reasoning_handler(data: str) -> None:
    print(data, end="", flush=True)    

async def main():
    """
    CLI Entry point. Initializes the asynchronous execution context.
    """
    configurator = CLISessionConfigurator()
    session_config = configurator.get_session_config()

    input_adapter = None

    if session_config.is_human:
        input_adapter = StandardInputSource()
    else:
        session_config.agent_params["on_reasoning"] = cli_reasoning_handler

    manager = DirectExecutionManager(session_config, input_adapter)

    async for event in manager.execute():
        handle_event(event)

def handle_event(event):
    match event:
        case GameStart(initial_observation=obs, game_name=name):
            print(f"\n--- Starting Game: {name} ---")
            print(f"Observation: {obs}")
        case GameTurn(iteration=it, action=act, observation=obs):
            print(f"\n--- Turn {it} ---\nAction: {act}\nObservation: {obs}")
        case GameResult(final_status=status, final_score=score):
            print(f"\n--- Game Ended: {status} ---\nFinal Score: {score}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n[!] Session interrupted by user. Exiting...")
        sys.exit(0)