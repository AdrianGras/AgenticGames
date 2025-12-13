from ui_layer.gradio.gradio_app import GameApp

if __name__ == "__main__":
    app = GameApp()
    demo = app.build_app_ui()
    demo.launch()
