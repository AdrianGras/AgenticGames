from games.level_based_games.mistery_secuences.mistery_secuences import MisterySecuences
from engine.core_engine import GameStatus


if __name__ == "__main__":
    game = MisterySecuences()
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
