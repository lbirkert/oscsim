from sim import Simulation
import pygame
import thorpy as tp

class UI:
    sim: Simulation
    gravity_enabled: tp.Checkbox
    gravity_x_input: tp.TextInput
    gravity_y_input: tp.TextInput

    def __init__(self, screen: pygame.Surface, sim: Simulation):
        self.sim = sim

        tp.init(screen, tp.theme_game1)
        gravity_text = tp.Text("Gravity")
        self.gravity_enabled = tp.Checkbox(self.sim.gravity_enabled)
        self.gravity_enabled.at_unclick = self.update_gravity_enabled
        x_text = tp.Text("X: ")
        self.gravity_x_input = tp.TextInput(str(self.sim.gravity.vec.x), placeholder="X")
        self.gravity_x_input.on_validation = self.update_gravity_x
        y_text = tp.Text("Y: ")
        self.gravity_y_input = tp.TextInput(str(self.sim.gravity.vec.y), placeholder="Y")
        self.gravity_y_input.on_validation = self.update_gravity_y
        unit_text = tp.Text("m/s^2")

        group = tp.Group([
            gravity_text, self.gravity_enabled, x_text, self.gravity_x_input, y_text, self.gravity_y_input, unit_text
        ], "h")

        settings = tp.TitleBox("Settings", [
            group,
        ])
        settings.center_on(screen)
        self.updater = settings.get_updater()

    def update_gravity_enabled(self):
        self.sim.gravity_enabled = not self.gravity_enabled.get_value()

    def update_gravity_x(self):
        try:
            self.sim.gravity.vec.x = float(self.gravity_x_input.get_value())
        except:
            pass
    
    def update_gravity_y(self):
        try:
            self.sim.gravity.vec.y = float(self.gravity_y_input.get_value())
        except:
            pass


    def update(self, events):
        self.updater.update(events=events)