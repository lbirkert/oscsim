from render import Render
from sim import Simulation
import pygame
import thorpy as tp

class UI:
    def __init__(self, render: Render):
        tp.init(render.screen, tp.theme_human)
        button = tp.Button("Hello, world (this button has no effect)")
        ddl = tp.DropDownListButton(("Blah", "Blah", "Blah blah"), "My list", bck_func=None)
        my_ui_elements = tp.Group([button, ddl])
        self.updater = my_ui_elements.get_updater()

    def update(self, events):
        self.updater.update(events)