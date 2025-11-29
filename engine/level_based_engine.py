from enum import Enum, auto
from engine.core_engine import CoreEngine, GameStatus
from abc import abstractmethod
import json

class LevelLogicResult(Enum):
    CONTINUE = auto()
    COMPLETED = auto()
    FAILED = auto()

class LevelBasedEngine(CoreEngine):
    def __init__(self):
        super().__init__()
        self.name = "Level Based Engine"
        self.max_unlocked_level = 0
        self.load_game_configuration()
        self.start_level(0)

    def load_game_configuration(self):
        """
        Loads the game configuration.
        """
        path = f"game_configs/{self.name.replace(' ', '_').lower()}.json"
        with open(path, 'r') as f:
            config = json.load(f)

        self.level_configs = config.get("levels", [])

    @property
    @abstractmethod
    def max_level_index(self):
        """
        Returns the maximum level index for the game.
        """
        return len(self.level_configs) - 1
    
    @abstractmethod
    def get_level_observation(self):
        """
        Returns the observation for the current level.
        """
        obs = f"\nYou are currently at level {self.current_level_index + 1}."
        return obs

    def get_initial_observation(self):
        """
        Returns the initial observation presented to the user.
        """
        initial_obs = super().get_initial_observation()
        initial_obs += self.get_level_observation()

        return initial_obs
    
    @abstractmethod
    def start_level(self, level_index):
        """
        Initializes the specified level.
        """
        self.current_level_index = level_index

    
    def get_instructions(self):
        """
        Returns the game instructions.
        """
        return (
            "This is a level based game!\n"
            "General Level movment instructions:\n"
            "1. You only have unlocked level 1.\n" \
            "2. In order to unlock level n, you must complete level n-1.\n"
            "3. Add /repeat at the beginning of your input to repeat the previous level.\n"
            "4. Add /level n at the beginning of your input to jump to level n if unlocked.\n"
        )
    
    @abstractmethod
    def apply_level_logic(self, input_data):
        """
        Applies the level logic based on the input data.
        """
        return LevelLogicResult.CONTINUE
    
    def process_input(self, input_data):
        if input_data[0] == '/':
            command_parts = input_data.split()
            command = command_parts[0]

            requested_level = None
            if command == '/repeat':
                requested_level = self.current_level_index - 1
            elif command == '/level' and len(command_parts) > 1:
                try:
                    requested_level = int(command_parts[1]) - 1
                except ValueError:
                    return "Invalid level number."
            else:
                return "Unknown command."
            return self.change_level(requested_level)  

        level_status = self.apply_level_logic(input_data)

        match level_status:
            case LevelLogicResult.COMPLETED:
                if self.current_level_index == self.max_level_index:
                    self.game_status = GameStatus.FINISHED
                    return "Congratulations! You have completed the final level of the game."
                self.max_unlocked_level = max(self.max_unlocked_level, self.current_level_index + 1)
                self.start_level(self.current_level_index + 1)
                return self.get_level_observation()
            
            case LevelLogicResult.CONTINUE:
                return self.get_level_observation()
            
            case LevelLogicResult.FAILED:
                self.game_status = GameStatus.FAILED
                return "You have failed the Game. Better luck next time!"
            

        return 
    
    def change_level(self, new_level_index):
        if new_level_index > self.max_level_index or new_level_index < 0:
            return f"Level {new_level_index + 1} does not exist."
        if new_level_index > self.max_unlocked_level:
            return f"Level {new_level_index + 1} is not unlocked yet."
        
        self.start_level(new_level_index)
        return self.get_level_observation()
    
    
        