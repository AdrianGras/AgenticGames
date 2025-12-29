---
title: AgenticGames
emoji: 🤖🎮
colorFrom: indigo
colorTo: purple
sdk: gradio
sdk_version: 5.49.1
app_file: app.py
pinned: false
license: apache-2.0
short_description: Framework for evaluating LLM agents in text-based games.
---

# AgenticGames

**AgenticGames** is a research-oriented framework designed for orchestrating, visualizing, and evaluating Artificial Intelligence (LLM) agent strategies within interactive game environments.

Unlike traditional benchmarks, this project focuses on **semantic feedback** and **autonomous adaptation**. Researchers can observe agent behavior in real-time, analyze reasoning traces, and benchmark AI performance against human gameplay in environments where the rules are not pre-defined in the agent's code.

[![Hugging Face Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-blue)](https://huggingface.co/spaces/Wifmin/AgenticGames)
> **Try it now:** If you want a quick test without installing anything, check out our [Public Demo on Hugging Face](https://huggingface.co/spaces/Wifmin/AgenticGames).

<p align="center">
  <img src="./assets/dashboard.gif" alt="AgenticGames Dashboard Demo" width="800">
  <br>
  <em>Real-time visualization of an LLM agent reasoning and playing through the Gradio Dashboard.</em>
</p>
---

## Project Architecture

The system is built on a four-layer modular architecture to ensure complete separation of concerns:

### 🎮 [Game Layer](./game_layer/)
Focuses on text-based environments with specific cognitive skill testing:
- **Zero-Knowledge Principle:** Games are designed to be played without prior instructions.
- **Pure Text Feedback:** No numerical scores are provided. Actors (agents or humans) must parse text strings to identify success, failure, or progress.
- **Skill Classification:** The games are classified based on cognitive skills like memory, long-term planning, pattern recognition, and more.

### 🧠 [Agent Layer](./agent_layer/)
Handles the "intelligence" and decision-making:
- **Reasoning Strategies:** Built-in support for Chain-of-Thought (CoT) and reasoning logs.
- **Extensible Models:** Currently suports OpenAI api and XAI, with easy integration for other LLMs.
- **Future-Ready:** Designed to extend capabilities with memory modules, tool use etc.

### ⚙️ [App Layer](./app_layer/)
The core engine that drives the execution:
- **The Game Loop:** Manages the flow between Game feedback and Agent responses.
- **UI Signaling:** Standardized structures for communication between the loop and the visual interfaces.

### 🖥️ [UI Layer](./ui_layer/)
Two distinct ways to interact with the system:
- **Gradio Dashboard:** A visual research tool with real-time reasoning logs, build modularly for extension.
- **CLI Interface:** A lightweight terminal-based version for fast testing and automated pipelines.

---

## 📝 Philosophy: Semantic Adaptation

The core challenge of **AgenticGames** is the removal of the "Reward Function" from the agent's reach. 

By using **text-only feedback**, we force the agent to behave like a human: interpreting context, learning from experience, and extracting necessary information autonomously. This allows for a deeper evaluation of an LLM's true reasoning capabilities rather than its ability to optimize a single number.

---
## Quick Start

### Prerequisites
- **Python 3.10+** installed on your system
- **LLM API Keys** for agent inference (OpenAI, XAI, or other supported providers—see [Agent Layer](./agent_layer/) for configuration details)
- **Git** for cloning the repository

### Installation Guide

Clone the repository and set up your development environment:

```bash
git clone https://github.com/Wifmin/AgenticGames.git
cd AgenticGames
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Agentic Mode Configuration

To initialize the agentic mode configuration, ensure that you set up the necessary API keys. These keys must be specified in the agent layer configuration to function properly.

Set your LLM API credentials in `.env`:
```
OPENAI_API_KEY=your_key_here
XAI_API_KEY=your_key_here
```
Specific instructions can be found in the [Agent Layer](./agent_layer/) documentation.


For detailed setup per component, see the respective layer documentation.

### Running AgenticGames

**Gradio Interface:**
```bash
python app.py
```
Open the URL displayed in your terminal to access the interactive research dashboard with real-time reasoning logs and game visualization.

**CLI Interface:**
Run this comand to use the cli interface in user mode and play the Mistery sequence game:
```bash
python ui_layer\cli\main.py --user_input --game mistery_sequences
```
You can also run the following comand to get further help:
```bash
python ui_layer\cli\main.py --help
```
Refer to [UI Layer](./ui_layer/) documentation for further details.


---

**License:** Apache-2.0
