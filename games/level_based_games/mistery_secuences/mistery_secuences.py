from engine.level_based_engine import LevelBasedEngine, LevelLogicResult

from .sequence_character import LetterA, LetterB

class MisterySecuences(LevelBasedEngine):
    def __init__(self):
        super().__init__()
        self.name = "Mistery Secuences Game"

    @property
    def max_level_index(self):
        return 4  

    def start_level(self, level_index):
        super().start_level(level_index)

        self.string_layout = self.level_configs[level_index].get("layout", [])
        level_character_layout = []
        for i, char in enumerate(self.string_layout):
            match char:
                case "A":
                    level_character_layout.append(LetterA(i))
                case "B":
                    level_character_layout.append(LetterB(i))
                
        self.level_character_layout = level_character_layout

    def get_level_observation(self):
        obs = super().get_level_observation()
        obs += "\nCurrent sequence: " + " ".join(self.string_layout)
        return obs
    
    def apply_level_logic(self, input_data):
        for character in self.level_character_layout:
            if not character.process_input(input_data):
                return LevelLogicResult.CONTINUE
                
        return LevelLogicResult.COMPLETED
                
