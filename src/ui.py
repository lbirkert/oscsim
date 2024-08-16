from sim import Simulation, Anchor, Spring
import pygame
import thorpy as tp

class SettingsUI:
    sim: Simulation
    gravity_enabled: tp.Checkbox
    gravity_x_input: tp.TextInput
    gravity_y_input: tp.TextInput
    settings: tp.TitleBox

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
        self.settings_updater = self.settings.get_updater()

        self.resize(screen)

    def resize(self, screen: pygame.Surface):
        width, height = screen.get_size()
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

    def update(self, events):
        self.settings_updater.update(events=events)

class AnchorUI:
    anchor: Anchor
    settings: tp.TitleBox

    def __init__(self, anchor: Anchor):
        self.anchor = anchor
        self.mass_input = tp.TextInput(str(anchor.get_mass()), placeholder="mass")
        self.mass_input.on_validation = self.update_mass
        mass_text = tp.Text("Mass: ")
        mass_unit = tp.Text("kg")
        mass = tp.Group([ mass_text, self.mass_input, mass_unit ], "h")
        reset_velocity = tp.Button("Reset velocity")
        reset_velocity.at_unclick = self.reset_velocity
        
        static_text = tp.Text("Static:")
        self.static_checkbox = tp.Checkbox(anchor.get_static())
        self.static_checkbox.at_unclick = self.update_static
        static = tp.Group([ static_text, self.static_checkbox ], "h")
        self.settings = tp.TitleBox("Anchor Settings", [
            static,
            mass,
            reset_velocity
        ])
        self.updater = self.settings.get_updater()
        self._show = False

    def resize(self, screen: pygame.Surface):
        width, height = screen.get_size()
        self.settings.center_on(pygame.Rect((0, height/2), (width, height/2)))

    def update(self, events):
        self.updater.update(events=events)
    
    def update_mass(self):
        try:
            self.anchor.set_mass(float(self.mass_input.get_value()))
        except:
            pass

    def update_static(self):
        self.anchor.set_static(not self.static_checkbox.get_value())

    def reset_velocity(self):
        self.anchor.vel = pygame.Vector2((0, 0))

class SpringUI:
    spring: Spring
    settings: tp.TitleBox

    def __init__(self, spring: Spring):
        self.spring = spring
        self.stiffness_input = tp.TextInput(str(spring.stiffness), placeholder="stiffness")
        self.stiffness_input.on_validation = self.update_stiffness
        stiffness_text = tp.Text("Stiffness: ")
        stiffness_unit = tp.Text("N/m")
        stiffness = tp.Group([ stiffness_text, self.stiffness_input, stiffness_unit ], "h")
        self.settings = tp.TitleBox("Spring Settings", [
            stiffness,
        ])
        self.updater = self.settings.get_updater()
        self._show = False

    def resize(self, screen: pygame.Surface):
        width, height = screen.get_size()
        self.settings.center_on(pygame.Rect((0, height/2), (width, height/2)))

    def update(self, events):
        self.updater.update(events=events)
    
    def update_stiffness(self):
        try:
            self.spring.stiffness = float(self.stiffness_input.get_value())
        except:
            pass
