---
title: AgenticGames
emoji: 🤖🎮
colorFrom: indigo
colorTo: slate
sdk: gradio
sdk_version: 4.44.1
app_file: app.py
pinned: false
license: apache-2.0
short_description: Research-oriented framework to test and evaluate AI agent strategies.
---

# 🤖 AgenticGames

**AgenticGames** is a research-oriented framework designed for orchestrating, visualizing, and evaluating Artificial Intelligence (LLM) agent strategies within interactive game environments.

The primary goal of this project is to provide a platform where researchers can observe agent behavior in real-time, analyze reasoning traces, and benchmark AI performance against human gameplay.

---

## 🚀 Key Features

* **Real-Time Visualization:** Interface specifically designed to monitor agent "Chain of Thought" and reasoning logs during gameplay.
* **Execution Control (Run Loop):** Fine-grained control allowing researchers to run agents step-by-step (Step Next) or in a continuous loop with instant pause capabilities.
* **Hybrid Mode:** Supports both autonomous agent play and manual user input modes for comparative studies.
* **Extensible Architecture:** Built on design patterns that simplify the integration of new models (OpenAI, Anthropic, local LLMs) and custom game environments.

---

## 🛠️ Setup & Installation

### Prerequisites
* Python 3.10 or higher.
* API Keys for the LLM providers you wish to test (optional for manual play mode).

### Local Installation
1. Clone the repository:
   ```bash
   git clone [https://github.com/Wifmin/AgenticGames.git](https://github.com/Wifmin/AgenticGames.git)
   cd AgenticGames