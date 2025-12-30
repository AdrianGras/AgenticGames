# ⚙️ App Layer: Orchestration & Execution

The **App Layer** acts as the central nervous system of the framework. It is responsible for assembling sessions, managing the asynchronous game loop, and providing flow control (Play/Pause/Step) to the UI and CLI layers.

---

## 🏗️ Core Components

The execution logic is divided into three main responsibilities:

### 1. Game Runner (`game_runner.py`)
The heart of the execution. It implements an **Asynchronous Generator** pattern that orchestrates the turn-based loop.
* **Decoupling:** It doesn't know about UIs or specific LLMs; it only knows how to pass an `Observation` from a `CoreEngine` to an `Actor` and return the resulting `Action`.
* **Events:** Instead of a closed loop, it yields structured **Domain Objects** (`GameStart`, `GameTurn`, `GameResult`) at every step.

### 2. Game Execution Manager (`game_execution_manager.py`)
A stateful manager that wraps the runner to provide advanced control for real-time interfaces.
* **Flow Control:** Implements a gate mechanism using `asyncio.Event` to support **Play**, **Pause**, and **Step** modes.
* **I/O Buffering:** Uses `asyncio.Queue` to decouple the high-speed game execution from the slower UI rendering and reasoning streams.
* **Reasoning Sink:** Captures internal agent "thoughts" via callbacks and queues them for asynchronous consumption by the UI.

### 3. Session Builders (`session_builder.py`)
Implements the **Builder Pattern** to abstract the complexity of instantiating and wiring a session.
* **HumanSessionBuilder:** Configures a runner with a `HumanActor` and its corresponding input adapter.
* **AgentSessionBuilder:** Configures a runner with an AI agent, injecting reasoning callbacks and LLM parameters.

---

## 📊 Domain Events (`runner_types.py`)

To ensure the UI Layer remains agnostic to the game logic, all data is passed as standardized dataclasses:

| Event | Yielded | Key Data |
| :--- | :--- | :--- |
| **`GameStart`** | Once (Start) | Initial scene description and game ID. |
| **`GameTurn`** | Every turn | Action taken, resulting observation, and iteration count. |
| **`GameResult`** | Once (End) | Final status (Finished/Failed) and full history log. |

---

## 🔄 The Execution Lifecycle



1.  **Configuration:** A `SessionConfig` object is passed to the `GameExecutionManager`.
2.  **Assembly:** The `SessionBuilder` fetches the correct game and agent from their respective factories.
3.  **Loop Initiation:** The `GameExecutionManager.start()` method begins consuming the runner's generator.
4.  **Flow Control:** 
    * In **Step mode**, the manager processes one yield and waits for a `_resume_event`.
    * In **Play mode**, the manager processes yields continuously.
5.  **Data Consumption:** The UI Layer polls `pop_pending_updates()` and `pop_reasoning()` to update the visual components.

---

## 📂 Directory Structure

```text
app_layer/
├── game_runner.py           # Core generator-based loop
├── game_execution_manager.py # Flow control and Queue management
├── session_builder.py       # Human and Agent factory logic
├── session_config.py        # Unified configuration dataclass
└── runner_types.py          # Standardized Domain Objects (Events)
```

---

