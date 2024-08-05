from sim import Simulation
import pygame
import thorpy as tp

class UI:
    sim: Simulation
    gravity_enabled: tp.Checkbox
    gravity_x_input: tp.TextInput
    gravity_y_input: tp.TextInput
    settings: tp.TitleBox
    anchor: tp.TitleBox
    spring: tp.TitleBox
    _show: bool

    def __init__(self, screen: pygame.Surface, sim: Simulation):
        self.sim = sim

        tp.init(screen, tp.theme_game1)
        gravity_text = tp.Text("Gravity")
        self.gravity_enabled = tp.Checkbox(self.sim.gravity_enabled)
        self.gravity_enabled.at_unclick = self.update_gravity_enabled
        x_text = tp.Text("X: ")
        self.gravity_x_input = tp.TextInput(str(self.sim.gravity.x), placeholder="X")
        self.gravity_x_input.on_validation = self.update_gravity_x
        y_text = tp.Text("Y: ")
        self.gravity_y_input = tp.TextInput(str(self.sim.gravity.y), placeholder="Y")
        self.gravity_y_input.on_validation = self.update_gravity_y
        unit_text = tp.Text("m/s^2")

        group = tp.Group([
            gravity_text, self.gravity_enabled, x_text, self.gravity_x_input, y_text, self.gravity_y_input, unit_text
        ], "h")

        self.settings = tp.TitleBox("Settings", [
            group,
        ])
        self.anchor_mass_input = tp.TextInput("1", placeholder="mass")
        self.anchor_mass_input.on_validation = self.anchor_update_mass
        anchor_mass_text = tp.Text("Mass: ")
        anchor_mass_unit = tp.Text("kg")
        anchor_mass = tp.Group([ anchor_mass_text, self.anchor_mass_input, anchor_mass_unit ], "h")
        anchor_reset_velocity = tp.Button("Reset velocity")
        anchor_reset_velocity.at_unclick = self.anchor_reset_velocity
        
        anchor_static_text = tp.Text("Static:")
        self.anchor_static_checkbox = tp.Checkbox(False)
        self.anchor_static_checkbox.at_unclick = self.anchor_update_static
        anchor_static = tp.Group([ anchor_static_text, self.anchor_static_checkbox ], "h")
        self.anchor_settings = tp.TitleBox("Anchor Settings", [
            anchor_static,
            anchor_mass,
            anchor_reset_velocity
        ])
        self.spring_settings = tp.TitleBox("Spring Settings", [

        ])

        self.settings_updater = self.settings.get_updater()
        self.anchor_settings_updater = self.anchor_settings.get_updater()
        self._show = False

        self.resize(screen)

    def toggle_show(self):
        self._show = not self._show

    def show(self):
        self._show = True

    def hide(self):
        self._show = False

    def resize(self, screen: pygame.Surface):
        width, height = screen.get_size()
        self.anchor_settings.center_on(pygame.Rect((0, height/2), (width, height/2)))
        self.settings.center_on(screen)

    def update_gravity_enabled(self):
        self.sim.gravity_enabled = not self.gravity_enabled.get_value()

    def update_gravity_x(self):
        try:
            self.sim.gravity.x = float(self.gravity_x_input.get_value())
        except:
            pass
    
    def update_gravity_y(self):
        try:
            self.sim.gravity.y = float(self.gravity_y_input.get_value())
        except:
            pass

    def anchor_update_mass(self):
        try:
            self.anchor.set_mass(float(self.anchor_mass_input.get_value()))
        except:
            pass

    def anchor_update_static(self):
        self.anchor.set_static(not self.anchor_static_checkbox.get_value())

    def anchor_reset_velocity(self):
        self.anchor.vel = pygame.Vector2((0, 0))

    def update(self, events):
        if not self._show:
            return

        self.settings_updater.update(events=events)

    def update_anchor(self, events, anchor):
        if not self._show:
            return

        self.anchor = anchor

        self.anchor_mass_input.set_value(str(anchor.get_mass()))
        self.anchor_static_checkbox.set_value(anchor.get_static())

        self.anchor_settings_updater.update(events=events)
