from games.level_based_games.mistery_secuences.mistery_secuences import MisterySecuences
GAMES = {
    "mistery_sequences": MisterySecuences,
}
def get_game(game_name):
    if game_name not in GAMES:
        raise ValueError(f"Game '{game_name}' not found.")

    return GAMES.get(game_name)()

def list_available_games():
    return list(GAMES.keys())