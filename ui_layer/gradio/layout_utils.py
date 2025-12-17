import gradio as gr
from contextlib import contextmanager

# =============================================================================
# MINIMALIST STRUCTURAL LAYOUT
# =============================================================================
_LAYOUT_CSS = """
/* No margin/padding on the container to avoid double spacing */
.layout-tight, .layout-wide {
    margin-left: auto !important;
    margin-right: auto !important;
    width: 100% !important;
}

/* Horizontal constraints */
.layout-tight {
    max-width: 650px !important;
}

.layout-wide {
    max-width: 1150px !important;
}

/* Padding interno para contenedores de texto con scroll */
.game-log-container {
    padding: 20px !important;
    overflow-y: auto !important; /* Asegura que el scroll funcione con el padding */
}

/* Opcional: Si quieres que el texto dentro del markdown no toque los bordes */
.game-log-container .prose {
    padding: 10px !important;
}
"""

def VSpacer(height: int = 20):
    """Simple vertical spacing."""
    return gr.Markdown(f"<div style='height: {height}px;'></div>")

def HSpacer(width: int = 20):
    """
    Horizontal spacer for Rows.
    Separates content Left from Right.
    
    Args:
        width: Minimum pixels of separation.
    """
    # scale=0 prevents the spacer from eating up more space than requested
    return gr.Column(min_width=width, scale=0)

class AppWindow(gr.Blocks):
    """Main window with minimal layout CSS."""
    def __init__(self, css: str = "", **kwargs):
        combined_css = f"{_LAYOUT_CSS}\n{css}"
        theme = gr.themes.Glass()
        super().__init__(theme = theme, css=combined_css, **kwargs)

@contextmanager
def TightCenteredLayout(visible: bool = True):
    """650px centered container."""
    with gr.Column(elem_classes=["layout-tight"], visible=visible) as col:
        yield col

@contextmanager
def WideCenteredLayout(visible: bool = True):
    """1150px centered container."""
    with gr.Column(elem_classes=["layout-wide"], visible=visible) as col:
        yield col