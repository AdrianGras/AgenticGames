import gradio as gr
from ui_layer.gradio.signals import SignalEmitter

class MisterySequencesInputView(SignalEmitter):

    def __init__(self):
        super().__init__()
        
        with gr.Column(elem_id="input-container"):
            # Display for the sequence
            self.input_box = gr.Textbox(
                label="Current Sequence",
                placeholder="Use buttons to build sequence...",
                interactive=False,
                show_copy_button=True
            )
            
            # --- Sequence Builder Row ---
            with gr.Row():
                self.btn_0 = gr.Button("Add 0", variant="secondary")
                self.btn_1 = gr.Button("Add 1", variant="secondary")
            with gr.Row():
                self.btn_clear = gr.Button("Clear", variant="stop")
                self.send_btn = gr.Button("Send Sequence", variant="primary")
            
            gr.Markdown("---") # Visual separator
            
            # --- Special Commands Section ---
            with gr.Row():
                    self.repeat_btn = gr.Button("🔄 Repeat Level")

            gr.Markdown("---") # Visual separator

            with gr.Row():
                self.level_btn = gr.Button("🚀 Go to Level")
                self.level_selector = gr.Number(
                    label="Level Number", 
                    value=1, 
                    precision=0, 
                    minimum=1,
                    step=1
                )

        # --- Logic Helpers ---

        def append_bit(current_val, bit):
            current_val = current_val or ""
            if current_val:
                return f"{current_val} {bit}"
            return str(bit)

        def clear_input():
            return ""

        # --- Event Wiring ---

        self.btn_0.click(fn=append_bit, inputs=[self.input_box, gr.State("0")], outputs=[self.input_box])
        self.btn_1.click(fn=append_bit, inputs=[self.input_box, gr.State("1")], outputs=[self.input_box])
        self.btn_clear.click(fn=clear_input, outputs=[self.input_box])

        on_send = self._send_on(self.send_btn.click, inputs=[self.input_box])
        on_send.then(fn=clear_input, outputs=[self.input_box])

        self._send_on(self.repeat_btn.click, inputs=[gr.State("/repeat")])
        self._send_on(self.level_btn.click, inputs=[self.level_selector], fn_process= lambda lvl: f"/level {int(lvl)}")
