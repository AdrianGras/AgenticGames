from engine.core_engine import CoreEngine
from abc import abstractmethod

class LevelBasedEngine(CoreEngine):
    def __init__(self):
        super().__init__()
        self.name = "Level Based Engine"
        self.current_level_index = 0
        self.max_unloecked_level = 0

    @property
    @abstractmethod
    def max_level_index(self):
        """
        Returns the maximum level index for the game.
        """
        return 0

    def get_initial_observation(self):
        """
        Returns the initial observation presented to the user.
        """
        initial_obs = super().get_initial_observation()
        initial_obs += f"\nYou are currently at level {self.current_level_index + 1}."
        return initial_obs
    
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
    
    def process_input(self, input_data):
        if input_data[0] == '/':
            command_parts = input_data.split()
            command = command_parts[0]

            if command == '/repeat':
                level_to_play = self.current_level_index - 1
            elif command == '/level' and len(command_parts) > 1:
                try:
                    requested_level = int(command_parts[1]) - 1
                except ValueError:
                    return "Invalid level number."
                
            if requested_level > self.max_level_index or requested_level < 0:
                return f"Level {requested_level + 1} does not exist."
            elif requested_level > self.max_unloecked_level:
                return f"Level {requested_level + 1} is not unlocked yet."
            
            return self.change_level(requested_level)  
            
        else:
            return "Unknown command."
        
        # TO DO
        return 
    
    def change_level(self, new_level_index):
        # TO DO
        pass