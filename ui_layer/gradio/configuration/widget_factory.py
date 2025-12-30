import gradio as gr
from typing import Any
from app_layer.registries.specs import (
    ParamSpec, IntParamSpec, FloatParamSpec, ChoiceParamSpec, BoolParamSpec
)

def create_widget(spec: ParamSpec) -> gr.Component:
    """
    Factory function that maps a ParamSpec to a corresponding Gradio component
    using structural pattern matching.

    Args:
        spec (ParamSpec): The domain parameter specification.

    Returns:
        gr.Component: The instantiated Gradio widget.
    """
    match spec:
        case IntParamSpec(label=label, description=info, default=val, min_value=mi, max_value=ma):
            return gr.Slider(
                label=label, info=info, value=val, 
                minimum=mi, maximum=ma, step=1, interactive=True
            )
            
        case FloatParamSpec(label=label, description=info, default=val, min_value=mi, max_value=ma, step=s):
            return gr.Slider(
                label=label, info=info, value=val, 
                minimum=mi, maximum=ma, step=s, interactive=True
            )
            
        case ChoiceParamSpec(label=label, description=info, default=val, choices=opts):
            return gr.Dropdown(
                label=label, info=info, choices=opts, 
                value=val, interactive=True
            )
            
        case BoolParamSpec(label=label, description=info, default=val):
            return gr.Checkbox(
                label=label, info=info, value=val, interactive=True
            )
            
        case _:
            # Fallback for unknown specification types
            return gr.Textbox(label=spec.label, value=str(spec.default), interactive=True)