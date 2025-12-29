# 🖥️ UI Layer

The **UI Layer** provides the interfaces through which users interact with the AgenticGames framework. It is decoupled from the game logic and agent decision-making, allowing for multiple ways to observe and control sessions.

Currently, the framework supports two distinct interfaces:

---

## 🛠️ Available Interfaces

### 1. [Gradio Dashboard](./gradio/)

**Recommended for research and visualization.**
The Gradio UI offers a rich, web-based experience where you can:

* **Real-time Reasoning:** See the agent's internal "thoughts" (tokens or logs) as they are generated.
* **Modular Components:** Select games, agents, and models from a user-friendly dashboard.
* **Visual Feedback:** View game observations and history in a structured layout.

**To run the Gradio dashboard:**

```bash
python app.py
```

Open the URL displayed in your terminal to access the interactive research dashboard with real-time reasoning logs and game visualization.


### 2. [CLI Interface](./cli/)

**Recommended for fast testing, automation, and hardcore users.**
The Command Line Interface is a lightweight tool built with `argparse`.

* **User Mode:** Play the games yourself directly from the terminal to test mechanics.
* **Agent Mode:** Run fast agent sessions without the overhead of a browser.
* **Automation:** Easy to integrate into scripts or pipes.

Run this comand to use the cli interface in user mode and play the Mistery sequence game:

```bash
python ui_layer\cli\main.py --user_input --game mistery_sequences
```

You can also run the following comand to get further help:

```bash
python ui_layer\cli\main.py --help
```

Refer to [CLI Interface](./cli) documentation for further details.

---

## 📂 Folder Structure

```text
ui_layer/
├── cli/            # Terminal-based interface logic
└── gradio/         # Web-based dashboard logic

```
