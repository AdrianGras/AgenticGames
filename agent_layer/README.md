# 🧠 Agent Layer

The **Agent Layer** manages the "intelligence" of the framework. It defines how different entities—whether human players or AI models—interact with the game environments.

---

## 🤖 Agent Catalog & Strategies

Agents are classified by their decision-making strategy and the cognitive depth of their reasoning. This catalog is a **Work In Progress**:

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

## Hierarchy & Core Classes

### 1. The Actor (`actor.py`)
The base abstract class for any entity.
* **Method:** `async def get_action(observation: str) -> str`.
* **Interchangeability:** Allows the orchestration layer to treat Humans and AI identicaly.

### 2. Human Actor (`human_actor.py`)
Enables manual play via UI or CLI. It uses an `InputSource` protocol to asynchronously fetch user commands.

### 3. Agent Actor (`agent_actor.py`)
Base for all AI entities. Adds the `emit_reasoning(data)` method to stream internal logic (thoughts, logs, tokens) to the UI via an optional callback.

### 4. LLM Agent (`llm_agents/llm_agent.py`)
A specialized bridge for Large Language Models.
* **Action Parsing:** Automatically extracts commands using the pattern `action: { command }`.
* **LLM Integration:** Holds an instance of a `GeneralLLM` client.

---

## 🔌 LLM Infrastructure (`agent_layer/llm_agents/LLMs/`)

To support multiple providers while keeping the code clean, the layer uses a provider-agnostic interface:

### General LLM (`general_llm.py`)
An abstract base class that enforces:
1. **Secure Credential Loading:** Automatically fetches API keys from `.env`.
2. **Standard Streaming:** Implements `stream_chat` to yield tokens asynchronously.

### LLM Selector (`llm_selector.py`)
A Factory pattern implementation. It maps model identifiers (e.g., `gpt-4`, `grok-4`) to their respective implementation classes (`OpenAILLM`, `GrokLLM`).

```
python
# Registering a new model is as simple as adding it to the MODELS dict:
MODELS = {
    "gpt-4": OpenAILLM,
    "grok-4": GrokLLM,
}
```


---



## 🛠️ How to Add a New LLM Provider

1. **Create a Client:** Inherit from `GeneralLLM` and implement `get_api_key_name`, `generate_client`, and `stream_chat`.
2. **Register:** Add your new class and model strings to the `MODELS` dictionary in `llm_selector.py`.
3. **Environment:** Add the required API key to your `.env` file.

