# 💻 CLI Interface

The **CLI (Command Line Interface)** is a lightweight, terminal-based entry point for the AgenticGames framework. It is designed for fast testing, automated sessions, and benchmarking without the overhead of a web browser.

<p align="center">
  <img src="../../assets/cli_demo.gif" alt="AgenticGames CLI Demo" width="700">
  <br>
  <em>A agent playing 'Mystery Sequences' and streaming reasoning directly in the terminal.</em>
</p>

---

## ✨ Features

* **Dual Mode:** Play manually as a human or let an AI agent take control.
* **Real-time Reasoning:** Streams the AI's internal thought process directly to the terminal.
* **Session Persistence:** Automatically saves every game session (input/output history) into organized text files for later analysis.
* **Safety Limits:** Prevents infinite loops in agent sessions with a configurable `max_iters` flag.

---

## 🚀 Usage

The CLI is executed via the `main.py` script. You must specify either a human user or an agent strategy.

### 1. Human Mode (Play yourself)
Use the `--user_input` flag to interact with the game via your keyboard.

```bash
python ui_layer/cli/main.py --game mistery_sequences --user_input
```


### 2. Agent Mode (AI play)
Specify an agent strategy and an LLM model.

```bash
python ui_layer/cli/main.py --game mistery_sequences --agent basic_agent --llm grok-4
```

---

## 🛠️ Command Line Arguments

| Argument | Required | Default | Description |
| :--- | :---: | :---: | :--- |
| `--game` | **Yes** | - | The identifier of the game (e.g., `mistery_sequences`). |
| `--agent` | No* | - | The AI agent strategy (e.g., `basic_agent`). |
| `--llm` | No | `gpt-4` | The LLM model identifier (e.g., `gpt-4`, `grok-4`). |
| `--user_input` | No* | - | Enables Human Mode (manual control). |
| `--max_iters` | No | `50` | Maximum number of turns allowed before stopping. |

> **Note:** You must provide either `--agent` OR `--user_input`, but not both.

---

## 📂 Output & History

The CLI automatically saves logs of every completed session. This is crucial for evaluating agent performance offline.

* **Storage Path:** `outputs/game_histories/{game_name}/`
* **Filename Format:** `session_{timestamp}_{agent_label}.txt`

Each log contains the full sequence of observations and actions, formatted for easy reading.
