from ui_layer.gradio.app import GradioApp

if __name__ == "__main__":
    app = GradioApp()
    demo = app.build()
    demo.launch()
