import gradio as gr
from ui_layer.gradio.signals import SignalEmitter

class StandardInputView(SignalEmitter):
    """
    UI Component for human interaction. 
    
    Responsible for capturing user text input and emitting it as a signal.
    It automatically clears the input field after a successful submission 
    using event chaining to prevent data loss.
    """

    def __init__(self):
        """
        Initializes the text input interface and wires internal events.
        """
        super().__init__()
        
        # 1. Component Definition
        with gr.Group():
            self.input_box = gr.Textbox(
                label="Your Action",
                placeholder="Type your command here...",
                show_label=False,
                container=False,
                interactive=True
            )
            self.send_btn = gr.Button("Send Action", variant="primary")

        # 2. Wiring with Chaining
        on_submit = self._send_on(self.input_box.submit, inputs=[self.input_box])
        on_click = self._send_on(self.send_btn.click, inputs=[self.input_box])

        # 3. Post-Emission Cleanup
        def _clear_input():
            return gr.update(value="")
        on_submit.then(fn=_clear_input, outputs=[self.input_box])
        on_click.then(fn=_clear_input, outputs=[self.input_box])