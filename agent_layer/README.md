# 🧠 Agent Layer

The **Agent Layer** is the "intelligence" hub of the framework. It orchestrates how different entities—from human players to advanced AI models—perceive and interact with game environments through a unified interface.

---

## 🚀 Quick Start (Configuration)

Before running any AI agents, you must configure your environment. The system automatically loads credentials from a `.env` file at the root of the project.

### 🔑 Required API Keys
Depending on the provider you wish to use, add these to your `.env`:

```bash
# OpenAI - Required for GPT-based agents
OPENAI_API_KEY=your_openai_key_here

# xAI - Required for Grok-based agents
XAI_API_KEY=your_xai_key_here
```

---

## 🤖 Agent Catalog & Strategies

Agents are classified by their decision-making strategy. You can swap them interchangeably in the orchestration layer.

| Agent | Strategy | Core Capability | Status |
| :--- | :--- | :--- | :--- |
| **Human Actor** | Manual Input | Human Baseline & Benchmarking | ✅ Operational |
| **Basic Agent** | Direct Prompting | Instruction following & Memory | ✅ Operational |
| **Search Agent** | Tree-of-Thought | State-space exploration | 🚧 Planned |
| **RAG Agent** | Vector Retrieval | Handling massive technical manuals | 🚧 Planned |
| **Graph-Scientist** | State Machine | Systematic hypothesis testing | 🚧 Planned |

---

## 📂 File Structure

```text
agent_layer/
├── actor.py                # Base unified interface
├── human_actor.py          # Human-in-the-loop implementation
├── agent_actor.py          # Base AI actor with reasoning support
└── llm_agents/             # LLM-specific implementations
    ├── llm_agent.py        # Bridge between AgentActor and LLM APIs
    ├── basic_agent/        
    │   ├── basic_agent.py  # Standard Agent with memory & prompts
    │   └── system_prompts.json # Library of agent behaviors
    └── LLMs/               
        ├── general_llm.py  # Provider-agnostic interface
        ├── llm_selector.py # Factory for instantiating clients
        ├── openai_llm.py   # OpenAI implementation
        └── grok_llm.py     # xAI implementation
```

---

##  Hierarchy & Core Classes

The architecture follows a strict inheritance pattern to ensure that the game engine doesn't care if it's talking to a human or a machine.

### 1. The Actor (`actor.py`)
The universal abstract base class.
* **Core Method:** `async def get_action(observation: str) -> str`.
* **Purpose:** Ensures total interchangeability between humans and AI.

### 2. Human Actor (`human_actor.py`)
Enables manual play. It uses an `InputSource` protocol to asynchronously fetch user commands via UI or CLI.

### 3. Agent Actor (`agent_actor.py`)
The base for all AI entities. It introduces `emit_reasoning(data)`, allowing the agent to stream its internal "thoughts" or logs to the UI separately from the final action.

### 4. LLM Agent (`llm_agents/llm_agent.py`)
A specialized bridge for Large Language Models.
* **Action Parsing:** Automatically extracts commands using the pattern `action: { command }`.
* **Integration:** Holds an instance of a `GeneralLLM` client.

---

## 🔌 LLM Infrastructure (`agent_layer/llm_agents/LLMs/`)

We use a provider-agnostic interface to support multiple LLMs simultaneously without bloating the logic.

### General LLM (`general_llm.py`)
An abstract base class that enforces:
1.  **Secure Credential Loading:** Automatically fetches the required key from `.env`.
    * **OpenAI:** Uses `OPENAI_API_KEY`.
    * **Grok:** Uses `XAI_API_KEY`.
2.  **Standard Streaming:** Implements `stream_chat` to yield tokens asynchronously across different SDKs.

### LLM Selector (`llm_selector.py`)
A Factory pattern implementation. Registering a new model is as simple as adding it to the `MODELS` dictionary:

```python
MODELS = {
    "gpt-4": OpenAILLM,   # Links to OpenAI implementation
    "grok-4": GrokLLM,    # Links to xAI implementation
}
```

---

## 🛠️ How to Add a New LLM Provider

1.  **Create a Client:** Inherit from `GeneralLLM` and implement `get_api_key_name`, `generate_client`, and `stream_chat`.
2.  **Register:** Add your new class and model strings to the `MODELS` dictionary in `llm_selector.py`.
3.  **Environment:** Add the required API key (e.g., `ANTHROPIC_API_KEY`) to your `.env` file.