from game_engine.core_engine import GameStatus
from games.game_selector import get_game, list_available_games
import sys
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <game_name>")
        print("Available games:")
        for game in list_available_games():
            print(f"- {game}")
        exit(1)
    game_name = sys.argv[1]
    game = get_game(game_name)
    initial_observation = game.start()
    print(initial_observation)
    while game.get_game_status() == GameStatus.RUNNING:
        user_input = input("Your input: ")
        try:
            observation = game.step(user_input)
            print(observation)
        except ValueError as e:
            print(f"Input Error: {e}")
            continue
