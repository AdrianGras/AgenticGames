# 🎮 Game Layer

The **Game Layer** is the foundation of AgenticGames. It provides the infrastructure to create text-based environments that challenge LLM cognitive capabilities.

---
## 📊 Game Catalog & Cognitive Mapping

Games are classified by the cognitive skills they evaluate. This is a **Work In Progress**:

| Game | Folder | Cognitive Skill | Status |
| :--- | :--- | :--- | :--- |
| **Mystery Sequences** | [/mistery_secuences](./games/level_based_games/mistery_secuences/README.md) | Scientific loop, Pattern Recognition | ✅ Playable (Levels WIP)|
| **Skewed Spinner** | TBD | Pattern recognition, resource planning | 🚧 Planned |
| **Technical Flight Manual** | TBD | Long term memory, resource planning | 🚧 Planned |

---
## 📂 File Structure

```text
game_layer/
├── game_engine/
│   ├── core_engine.py          # Abstract Base Class
│   └── level_based_engine.py   # Engine for level-based logic
├── game_configs/               # JSON files with level definitions
├── games/                      # Game implementations
│   ├── level_based_games/      # Games inheriting from LevelBasedEngine
│   │   └── mistery_sequences/
│   └── game_selector.py        # Factory for instantiating games
```

---
##  Game Engines

The system uses an inheritance-based architecture to facilitate the creation of different types of challenges:

### 1. Core Engine (core_engine.py)
The Abstract Base Class for all games. It manages the game loop state, history tracking, and basic lifecycle.

**Mandatory methods to implement:**
* **@property name**: Returns the unique identifier string of the game.
* **get_instructions()**: Returns the initial rules/context provided to the actor.
* **verify_input(input_data)**: Validates the input format before processing.
* **process_input(input_data)**: The core logic. Receives an action and returns a text observation.

### 2. Level Based Engine (level_based_engine.py)
An extension of the Core Engine designed for games divided into progressive levels. It automates JSON configuration loading and navigation logic.

**Integrated Features:**
* **System Commands**: Native support for `/repeat` (to replay the previous level) and `/level n` (to jump to a specific unlocked level).
* **State Management**: Automatically handles `LevelLogicResult` (CONTINUE, COMPLETED, FAILED).
* **External Config**: Automatically loads level data from `game_layer/game_configs/{game_name}.json`.

---



## 🛠️ How to Add a New Game

To add a new challenge to the framework, follow these steps:

### 1. Implement the Logic
Create a new folder in `games/` (or `games/level_based_games/`) and inherit from the appropriate class.

```python
from game_layer.game_engine.level_based_engine import LevelBasedEngine, LevelLogicResult

class MyNewGame(LevelBasedEngine):
    @property
    def name(self):
        return "my_new_game"

    def verify_level_input(self, input_data):
        # Your validation logic here (e.g., check if input is a number)
        pass

    def apply_level_logic(self, input_data):
        # Your game logic here
        # Return LevelLogicResult.COMPLETED, CONTINUE, or FAILED
        return LevelLogicResult.COMPLETED 
```
### 2. Register the Game
You must register the new game in `game_layer/games/game_selector.py` so the UI and CLI can find it:

```python
from game_layer.games.level_based_games.my_new_game.script import MyNewGame

GAMES: dict[str, Type[CoreEngine]] = {
    "mistery_sequences": MisterySecuences,
    "my_new_game": MyNewGame,  # <-- Register here
}
```


> **Note:** Each game folder should contain its own `README.md` explaining the specific logic, level structure, and intended evaluation metrics.
