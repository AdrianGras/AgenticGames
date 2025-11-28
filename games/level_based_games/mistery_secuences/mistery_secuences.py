from engine.level_based_engine import LevelBasedEngine, LevelLogicResult

class MisterySecuences(LevelBasedEngine):
    def __init__(self):
        super().__init__()
        self.name = "Mistery Secuences Game"

    @property
    def max_level_index(self):
        return 4  

    def start_level(self, level_index):
        super().start_level(level_index)

        level_character_layout = self.level_configs[level_index].get("layout", [])


