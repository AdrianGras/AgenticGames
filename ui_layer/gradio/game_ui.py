import gradio as gr
from abc import ABC, abstractmethod


class GameUI(ABC):
    def __init__(self, game_name, widget_column):
        self.name = game_name
        self.widget_col = widget_column


    def build(self):
        with self.widget_col:
            gr.Markdown(self.name)
            self.build_observations_display()

    @abstractmethod
    def build_observations_display():
        pass

    @abstractmethod
    def update_observations(new_observation):
        pass
