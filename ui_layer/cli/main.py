import asyncio
import argparse
import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any

# Path alignment to include project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from app_layer.session_builder import SessionBuilder, HumanSessionBuilder, AgentSessionBuilder
from app_layer.runner_types import GameStart, GameTurn, GameResult
from game_layer.games.game_selector import list_available_games
from agent_layer.agent_selector import list_available_agents

# Configuration Constants
OUTPUT_DIR = os.path.join("outputs", "game_histories")


class CLIInputAdapter:
    """
    Standard input adapter for the Command Line Interface.
    """
    async def get(self) -> str:
        return await asyncio.to_thread(input, "\n>> Enter action: ")
    
async def console_reasoning_printer(token: str):
    """Callback to print AI thoughts in real-time."""
    print(token, end="", flush=True)

def parse_arguments() -> argparse.Namespace:
    """
    Defines and parses the command-line arguments for the session.
    """
    parser = argparse.ArgumentParser(description="AI Game Agent - CLI Launcher")
    
    parser.add_argument(
        "--game", 
        required=True, 
        choices=list_available_games(),
        help="The identifier of the game to play."
    )
    
    parser.add_argument(
        "--agent", 
        choices=list_available_agents(), 
        help="The AI agent strategy to use."
    )
    parser.add_argument(
        "--llm", 
        default="mock", 
        help="The LLM model identifier (e.g., 'gpt-4', 'grok-beta'). Default is 'mock'."
    )
    
    parser.add_argument(
        "--user_input", 
        action="store_true", 
        help="If set, enables Human Mode (manual control)."
    )

    parser.add_argument(
        "--max_iters", 
        type=int, 
        default=50, 
        help="Safety limit for the maximum number of turns."
    )

    args = parser.parse_args()

    if args.user_input and args.agent:
        parser.error("Conflict: Cannot specify both --user_input and --agent.")
    if not args.user_input and not args.agent:
        parser.error("Requirement: Must specify either --agent or --user_input.")
    
    return args

def save_session_history(history: str, game_name: str, agent_label: str) -> None:
    """
    Persists the game log to a text file.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder = os.path.join(OUTPUT_DIR, game_name)
    os.makedirs(folder, exist_ok=True)
    
    filename = f"session_{timestamp}_{agent_label}.txt"
    filepath = os.path.join(folder, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(history)
    
    print(f"\n[System]: Session history saved to: {filepath}")

async def main():
    args = parse_arguments()

    builder: SessionBuilder
    agent_label: str

    if args.user_input:
        adapter = CLIInputAdapter()
        builder = HumanSessionBuilder(
            game_name=args.game,
            input_adapter=adapter,
        )
        agent_label = "Human"
    else:
        agent_params = {
            "model_name": args.llm,
            "on_reasoning": console_reasoning_printer
        }
        builder = AgentSessionBuilder(
            game_name=args.game,
            agent_name=args.agent,
            agent_params=agent_params
        )
        agent_label = f"{args.agent}_{args.llm}"

    try:
        print(f"--- Initializing {args.game} for {agent_label} ---")
        runner = builder.build()
    except ValueError as e:
        print(f"[CRITICAL ERROR]: Could not build session. {e}")
        return
    
    try:
        async for event in runner.run():
            # --- SCENE START ---
            if isinstance(event, GameStart):
                print("\n" + "="*60)
                print(f"GAME START: {event.game_name}")
                print("="*60)
                print(f"\n{event.initial_observation}\n")

            # --- TURN EXECUTION ---
            elif isinstance(event, GameTurn):
                print(f"> Action: {event.action}")
                print("-" * 20)
                print(f"{event.observation}\n")

                if event.iteration >= args.max_iters:
                    print(f"\n[System]: Max iterations limit ({args.max_iters}) reached. Stopping.")
                    break

            # --- GAME OVER ---
            elif isinstance(event, GameResult):
                print("="*60)
                print(f"GAME OVER")
                print(f"Status: {event.final_status.name}")
                print("="*60)
                
                save_session_history(event.history_log, args.game, agent_label)

    except KeyboardInterrupt:
        print("\n\n[System]: Session interrupted by user (Ctrl+C).")
    except Exception as e:
        print(f"\n[System]: Unexpected runtime error: {e}")

if __name__ == "__main__":
    asyncio.run(main())