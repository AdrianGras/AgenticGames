# ⚙️ App Layer: Orchestration & Execution

The App Layer serves as the primary bridge between the User Interface and the Domain (Games and Agents). Beyond simple mediation, it is responsible for orchestrating the interaction between the Agent and the Game engine.

---

## 🏗️ Core Components

The application logic is divided into four main areas of responsibility:

### 1. Core Logic (`app_layer/core/`)
Contains the fundamental and immutable elements of the game lifecycle.
* **Game Runner (`runner.py`):** The heart of the execution. It implements an **Asynchronous Generator** pattern that orchestrates the turn-based loop.
* **Domain Types (`types.py`):** Defines standardized data objects (`GameStart`, `GameTurn`, `GameResult`) ensuring the UI remains agnostic to internal logic.

### 2. Execution Management (`app_layer/execution/`)
Manages the different modes in which a session can be processed.
* **Managers (`/managers/`):** 
    * **Controlled:** Designed for UIs; allows **Pausing** and **Step-by-Step** execution via asynchronous events.
    * **Direct:** A simplified flow for continuous execution without manual intervention.
* **Agent Evaluator (`evaluator.py`):** A benchmark simulation engine capable of running multiple sessions in parallel using independent processes.

### 3. Session Building (`app_layer/building/`)
Implements the **Builder Pattern** to abstract the complexity of instantiation.
* **Session Builder:** Configures the runner by injecting the correct actors, input adapters, and game parameters.
* **Registries:** An automated discovery system that locates available games and agents by scanning `manifest.py` files.

### 4. I/O Adapters (`app_layer/io/`)
Defines how information flows between the user and the system.
* **Input Source:** Abstract interfaces for receiving user input (e.g., CLI, Gradio).
* **Async InputB ridgee:** A synchronized buffer that allows data input from asynchronous interfaces (like Gradio) into the game loop safely.

---

## 📊 Domain Events (`core/types.py`)

To ensure the UI Layer remains agnostic to the game logic, all data is passed as standardized dataclasses:

| Event | Yielded | Key Data |
| :--- | :--- | :--- |
| **`GameStart`** | Once (Start) | Initial scene description, game name, and base score. |
| **`GameTurn`** | Every turn | Action taken, engine response, and current score. |
| **`GameResult`** | Once (End) | Final status (Finished/Failed) and full historical log. |

---

## 🔄 The Execution Lifecycle



1. **Configuration:** A `SessionConfig` is received, defining the participants (Human/Agent) and the game environment.
2. **Assembly:** The `SessionBuilder` resolves dependencies via the `Registry` and assembles the `GameRunner` with the appropriate `Actor` (the agent or human) and `CoreEngine` (the game).
3. **Supervision:** An `ExecutionManager` (Direct or Controlled) wraps the runner to provide an interface tailored to the caller's execution requirements.
4. **Orchestration:** The manager drives the `GameRunner` generator. During this phase, the App Layer manages the ping-pong of data: Observations are sent to Actors, and Actions are returned to the Game Engine.
5. **Event Propagation:** Game events and internal reasoning (thoughts) are captured by the manager and propagated to the final consumer (UI components, CLI, or statistical aggregators).
---

## 📂 Directory Structure

```text
app_layer/
├── building/
│   ├── session_builder.py
│   └── session_config.py
├── core/
│   ├── game_runner.py
│   └── runner_types.py
├── execution/
│   ├── managers/
│   │   ├── controlled_execution_manager.py
│   │   └── direct_execution_manager.py
│   └── agent_evaluator.py
├── io/
│   ├── async_input_bridge.py
│   └── input_source.py
└── registries/
    ├── discovery.py
    ├── generic_registry.py
    ├── manager.py
    └── specs.py
```