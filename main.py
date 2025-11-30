from game_layer.game_engine.core_engine import GameStatus
from game_layer.games.game_selector import get_game, list_available_games
from agent_layer.agents.agent_selector import get_agent, list_available_agents
from agent_layer.LLMs.openai_llm import OpenAILLM

import sys
import argparse
import os

MAX_ITERS = 50

def parse_args():
    available_games = list_available_games()
    available_agents = list_available_agents()

    parser = argparse.ArgumentParser(
        description="Game launcher with agent or user input."
    )
    parser.add_argument(
        "--game",
        required=True,
        choices=available_games,
        help=f"Game name. Options: {', '.join(available_games)}",
    )
    parser.add_argument(
        "--agent",
        choices=available_agents,
        help=f"Agent name. Options: {', '.join(available_agents)}",
    )
    parser.add_argument(
        "--user_input",
        action="store_true",
        help="If specified, actions will be requested from console instead of using an agent.",
    )

    args = parser.parse_args()

    if not args.user_input and args.agent is None:
        parser.error("You must specify --agent NAME or use --user_input.")

    if args.user_input and args.agent is not None:
        print("Warning: --user_input was specified, --agent will be ignored.")

    return args

def save_game_and_close(game, agent_name, game_name):
    game_history = game.get_full_history()
    save_folder = os.path.join("outputs", "game_histories", game_name)
    os.makedirs(save_folder, exist_ok=True)
    index = len(os.listdir(save_folder))
    save_path = os.path.join(save_folder, f"history_{index}.txt")

    with open(save_path, "w") as f:
        content = f"# Game History for {game_name}, using agent: {agent_name}\n\n"
        content += game_history
        f.write(content)

if __name__ == "__main__":
   
    args = parse_args()

    if not args.user_input:
        llm = OpenAILLM()
        agent = get_agent(args.agent, llm)

    game = get_game(args.game)

    observation = game.start()
    print(observation)

    iteration = 0
    while game.get_game_status() == GameStatus.RUNNING:
        if args.user_input:
            action = input("Enter your action: ")
        else:
            action = agent.get_action(observation)
        try:
            observation = game.step(action)
            if not args.user_input:
                print(action)
            print(observation)
        except ValueError as e:
            print(f"Input Error: {e}")
            continue
        iteration += 1
        if iteration >= MAX_ITERS:
            print("Maximum iterations reached. Ending game.")
            break

    game_history = game.get_full_history()
    save_folder = os.path.join("outputs", "game_histories", args.game)
    os.makedirs(save_folder, exist_ok=True)
    index = len(os.listdir(save_folder))
    save_path = os.path.join(save_folder, f"history_{index}.txt")

    with open(save_path, "w") as f:
        content = f"# Game History for {args.game}, using agent: {args.agent if not args.user_input else 'user input'}\n\n"
        content += game_history
        f.write(content)
