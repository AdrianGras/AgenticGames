import gradio as gr
import uuid

# Global CSS for the main window (resetting defaults)
_GLOBAL_APP_CSS = """
.gradio-container {
    min-height: 100vh !important;
}
footer {
    display: none !important;
}
"""

class AppWindow(gr.Blocks):
    """
    A specialized Gradio Blocks window pre-configured with global application styles.
    
    Inherits from gr.Blocks, so it accepts all standard arguments (theme, title, etc.).
    """
    def __init__(self, css: str = "", **kwargs):
        # Merge custom CSS with our global base CSS
        combined_css = f"{_GLOBAL_APP_CSS}\n{css}"
        
        # Initialize the parent Blocks class with our settings
        super().__init__(css=combined_css, fill_height=True, **kwargs)

from gradio.events import Dependency

class CenteredGroup(gr.Group):
    """
    A container that centers its content and constrains the maximum width.
    
    It generates a unique ID and injects a scoped style tag to handle layout 
    without polluting global CSS.
    
    Args:
        width (int): The maximum width in pixels. Defaults to 800.
        **kwargs: Standard arguments for gr.Group (visible, elem_id, etc.)
    """
    def __init__(self, width: int = 800, **kwargs):
        self.target_width = width
        
        # Generate a unique ID if one wasn't provided by the user.
        # We need this ID to target this specific group with CSS.
        if "elem_id" not in kwargs:
            kwargs["elem_id"] = f"center-group-{str(uuid.uuid4())[:8]}"
        
        super().__init__(**kwargs)

    def __enter__(self):
        """
        When entering the 'with' block, we inject the specific CSS for this group.
        """
        # 1. Activate the group context
        result = super().__enter__()
        
        # 2. Define the CSS rules specifically for this element's ID
        # flex-grow: 0 prevents Gradio from stretching it.
        # margin: 0 auto handles the horizontal centering.
        scoped_css = f"""
        <style>
            #{self.elem_id} {{
                max-width: {self.target_width}px !important;
                width: 100% !important;
                margin-left: auto !important;
                margin-right: auto !important;
                flex-grow: 0 !important;
            }}
        </style>
        """
        
        # 3. Inject the style invisibly inside the group
        gr.HTML(scoped_css, visible=False)
        
        return result
    from typing import Callable, Literal, Sequence, Any, TYPE_CHECKING
    from gradio.blocks import Block
    if TYPE_CHECKING:
        from gradio.components import Timer
        from gradio.components.base import Component