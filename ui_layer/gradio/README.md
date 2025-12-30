---
title: Gradio UI Layer
---

# 🎨 Gradio UI Layer: Modular View Architecture

The Gradio interface is built on a **Decoupled View Architecture**. The dashboard is not a static layout, but a dynamic assembly of three independent functional modules that communicate through a synchronized signal bus.

---

## 🏗️ Core UI Modules

Every session is composed of three specialized modules. Each has a dedicated **Selector** (Factory) and a **Standard Fallback** implementation to ensure system stability regardless of the game or agent complexity.

| Module | **Game View** | **Input View** | **Agent View** |
| :--- | :--- | :--- | :--- |
| **Responsibility** | Environment state rendering. | User command capture. | Reasoning trace & flow control. |
| **Interface Class** | `SignalReceiver` | `SignalEmitter` | `AgentControlBaseUI` |
| **Data Flow** | Downstream (Observations). | Upstream (Action Commands). | Bi-directional (Flow / Thoughts). |
| **Fallback** | `StandardGameView` | `StandardInputView` | `StandardAgentUI` |

---

## 🛠️ Implementation Contracts

To extend the interface, a new component must inherit from the appropriate base class and fulfill its technical contract.

### 1. Game View Modules (`SignalReceiver`)
Responsible for transforming raw domain data into visual representations.
* **Contract:** Define layout in `__init__`, pass components to `super().__init__(targets=...)`, and implement `update(self, data)`.

```python
class CustomGameView(SignalReceiver):
    def __init__(self, game_name: str):
        with gr.Group():
            gr.Markdown(f"### 🎮 Playing: {game_name}")
            self.display = gr.Chatbot(type="messages")
        
        # Mandatory: Register which components are updated by this receiver
        super().__init__(targets=[self.display])

    def update(self, data):
        # Logic to transform game data into UI updates
        return [{"role": "assistant", "content": data}]
```

### 2. Input View Modules (`SignalEmitter`)
Responsible for providing interaction mechanisms (Buttons, D-Pads, etc.).
* **Contract:** Call `self._send_on()` in `__init__` to wire events.

```python
class CustomInputView(SignalEmitter):
    def __init__(self):
        super().__init__()
        self.btn = gr.Button("Execute")
        # Wire the event to the signal bus
        self._send_on(self.btn.click, inputs=None, fn_process=lambda: "action_id")
```

### 3. Agent View Modules (`AgentControlBaseUI`)
Hybrid modules that manage reasoning visualization and session lifecycle.
* **Contract:** Implement `_build_reasoning_layout()` AND `update(self, data)`.

```python
class CustomAgentUI(AgentControlBaseUI):
    def _build_reasoning_layout(self) -> List[gr.Component]:
        # Define layout and return components that will act as SignalReceiver targets
        self.reasoning_box = gr.Chatbot(type="tuples")
        return [self.reasoning_box] 

    def update(self, data: Any):
        # Format and return the new state for reasoning_box
        return [ (None, f"Thought: {data}") ]
```

---

## 🧩 Dynamic Registry & Selectors

Each module type utilizes a registry within its `selector.py`. To activate a specialized UI, the class must be mapped to the corresponding game identifier.



**Example: Registry Configuration**
```python
# ui_layer/gradio/game_session/input_views/input_ui_selector.py
INPUT_UIs: Dict[str, Type[SignalEmitter]] = {
    "mistery_sequences": MisterySequencesInputView,
    "logic_gates": LogicGatesInputView  
}
```

---

## 📂 Symmetrical Directory Structure

```text
gradio/game_session/
├── game_views/      # Receivers: Rendering environmental feedback.
│   ├── game_ui_selector.py
│   └── standard_game_view.py
├── input_views/     # Emitters: Capturing user interaction.
│   ├── input_ui_selector.py
│   └── standard_input_view.py
└── agent_views/     # Hybrid: Reasoning streaming & Session lifecycle.
    ├── agent_control_base_ui.py
    └── standard_agent_ui.py
```
