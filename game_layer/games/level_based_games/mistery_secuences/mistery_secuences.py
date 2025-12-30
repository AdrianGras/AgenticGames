from game_layer.game_engine.level_based_engine import LevelBasedEngine, LevelLogicResult
from .sequence_character import CHAR_MAP

class MisterySecuences(LevelBasedEngine):
    def __init__(self, max_consecutive_failed_attempts: int = 50):
        super().__init__()
        self.max_consecutive_failed_attempts = max_consecutive_failed_attempts
        self.current_consecutive_failed_attempts = 0
    
    @property
    def name(self):
        return "Mistery Sequences"

    def start_level(self, level_index):
        super().start_level(level_index)

        self.string_layout = self.level_configs[level_index].get("layout", [])
        level_character_layout = []

        for i, char in enumerate(self.string_layout):
            if char in CHAR_MAP:
                character_instance = CHAR_MAP[char](position=i)
                level_character_layout.append(character_instance)
                
        self.level_character_layout = level_character_layout

    def get_level_observation(self):
        obs = super().get_level_observation()
        if self.steps_in_current_level > 0:
            obs += "\nWrong answer, try again."
        else:
            obs += "\nCurrent sequence: " + " ".join(self.string_layout)
        return obs
    
    def apply_level_logic(self, input_data):
        input_data = [int(x) for x in input_data.split()]
        for character in self.level_character_layout:
            if not character.check_sequence(input_data):
                return self._handle_not_completed()
        
        for x in input_data:
            if x == 1:
                self.current_consecutive_failed_attempts = 0
                return LevelLogicResult.COMPLETED
        
        return self._handle_not_completed()
    
    def _handle_not_completed(self):
        self.current_consecutive_failed_attempts += 1
        if self.current_consecutive_failed_attempts >= self.max_consecutive_failed_attempts:
            return LevelLogicResult.FAILED
        else:   
            return LevelLogicResult.CONTINUE
    
    def get_instructions(self):
        inst = super().get_instructions()
        inst += (
            "Welcome to the Mistery Secuences Game!\n"
            "In each level, you will be presented with a sequence of characters.\n"
            "Your answer must be a sequence of 0 and 1 with the same length, separated by spaces.\n"
            "Example: '1 0 1 1 0'\n"
        )
        return inst
    
    def verify_level_input(self, input_data):
        input_parts = input_data.split()
        if len(input_parts) != len(self.string_layout):
            raise ValueError(f"The length of the current sequence is {len(self.string_layout)}, and hence, your input must have {len(self.string_layout)} elements separated by spaces.")
        for part in input_parts:
            if part not in ["0", "1"]:
                raise ValueError("Each element in the input must be either 0 or 1.")