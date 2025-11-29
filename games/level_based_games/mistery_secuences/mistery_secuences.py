from game_engine.level_based_engine import LevelBasedEngine, LevelLogicResult

from .sequence_character import LetterA, LetterB

class MisterySecuences(LevelBasedEngine):
    def __init__(self):
        super().__init__()
    
    @property
    def name(self):
        return "Mistery Sequences"

    def start_level(self, level_index):
        super().start_level(level_index)

        self.string_layout = self.level_configs[level_index].get("layout", [])
        level_character_layout = []

        CHAR_MAP = {
            "A": LetterA,
            "B": LetterB,
        }
        for i, char in enumerate(self.string_layout):
            if char in CHAR_MAP:
                character_instance = CHAR_MAP[char](position=i)
                level_character_layout.append(character_instance)
                
        self.level_character_layout = level_character_layout

    def get_level_observation(self):
        obs = super().get_level_observation()
        obs += "\nCurrent sequence: " + " ".join(self.string_layout)
        return obs
    
    def apply_level_logic(self, input_data):
        input_data = [int(x) for x in input_data.split()]
        for character in self.level_character_layout:
            if not character.check_sequence(input_data):
                return LevelLogicResult.CONTINUE
                
        return LevelLogicResult.COMPLETED
    
    def get_instructions(self):
        inst = super().get_instructions()
        inst += (
            "Welcome to the Mistery Secuences Game!\n"
            "In each level, you will be presented with a sequence of characters.\n"
            "Your answer must be a sequence of 0 and 1 with the same length, separated by spaces.\n"
        )
        return inst
    
    def verify_input(self, input_data):
        super().verify_input(input_data)
        input_parts = input_data.split()
        if len(input_parts) != len(self.string_layout):
            raise ValueError(f"Input must have {len(self.string_layout)} elements separated by spaces.")
        for part in input_parts:
            if part not in ["0", "1"]:
                raise ValueError("Each element in the input must be either '0' or '1'.")