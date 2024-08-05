from typing import List, Tuple
from abc import ABC, abstractmethod
from render import Render
import pygame
import threading
import time
import math

# describes how fine the simulation runs
TIMESTEP = 0.01
# describes at which speed the simulation runs compared to the real time
SIM_TO_REAL = 1

class Force:
    def __init__(self, vec):
        self.vec = pygame.Vector2(vec)

    # Returns the force/antiforce pair
    def pair(vec) -> Tuple['Force', 'Force']:
        vec = pygame.Vector2(vec)
        return Force(vec), Force(-vec)

# An anchor is a point on which force can be applied to for moving the point
class Anchor:
    selected: bool

    def __init__(self, pos=(0,0), vel=(0,0), static=False, lock=False, mass=1):
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(vel)
        self._static = static
        self._lock = lock
        # in kilograms
        self.mass = mass
        self.selected = False
        self.update_coef()
        self.update_radius()

    def update_coef(self):
        self.coef = 0 if self._static or self._lock else 1 / self.mass

    def update_radius(self):
        SIZE_RATIO = 0.10876
        self.radius = math.sqrt(self.mass) * SIZE_RATIO
    
    # Apply a force to this anchor
    # F = m * a
    def apply(self, force: Force):
        self.vel += TIMESTEP * self.coef * force.vec
    
    # Update the position of this anchor
    def update(self):
        self.pos += TIMESTEP * self.vel

    def set_static(self, val: bool):
        self._static = val
        if self._static:
            self.vel = pygame.Vector2((0, 0))
        self.update_coef()

    def lock(self):
        self._lock = True
        self.coef = 0
        self.vel = pygame.Vector2((0, 0))

    def unlock(self):
        self._lock = False
        self.update_coef()

    def get_rect(self, render: Render):
        center = render.transform_point(self.pos)
        radius = render.transform_size(self.radius)

        return pygame.Rect(center - pygame.Vector2(radius, radius), (2 * radius, 2 * radius))

    def render(self, render: Render):
        if self.selected:
            color = (0, 255, 100)
        elif self._static:
            color = (150, 150, 150)
        else:
            color = (255, 255, 255)

        render.draw_circle(color, self.pos, self.radius)

class Spring(ABC):
    start: Anchor
    end: Anchor

    def __init__(self, **kwargs):
        self.start = kwargs.get("start", Anchor((0, 0)))
        self.end = kwargs.get("end", Anchor(self.start.pos))
        self.max_force = kwargs.get("max_force")
        self.min_force = kwargs.get("min_force")

        assert isinstance(self.start, Anchor)
        assert isinstance(self.end, Anchor)

    # returns the magnitude of the force this spring applies based on the compression
    @abstractmethod
    def magnitude(self, dist: float) -> float:
        pass

    def force(self) -> Tuple[Force, Force]:
        delta = self.end.pos - self.start.pos
        dist = delta.magnitude()
        if dist == 0:
            return Force.pair((0, 0))
        magnitude = self.magnitude(dist)
        if self.max_force is not None:
            magnitude = min(self.max_force, magnitude)
        if self.min_force is not None:
            magnitude = max(self.min_force, magnitude)
        return Force.pair(delta * (magnitude / dist))

    def apply(self):
        start_force, end_force = self.force()
        self.start.apply(start_force)
        self.end.apply(end_force)
    
    def render(self, render: Render):
        SPRING_WIDTH = 0.2
        SEGS = 20
        delta = self.end.pos - self.start.pos
        dist = delta.magnitude()
        if dist == 0:
            return
        delta_n = delta / dist
        normal = pygame.Vector2(-delta_n.y, delta_n.x)

        points = []
        points.append(self.start.pos)

        # 10 zigzag segments
        for i in range(1, SEGS):
            off_delta = (i / SEGS) * delta
            off_normal = SPRING_WIDTH * (normal if i % 2 == 0 else -normal)
            points.append(self.start.pos + off_delta + off_normal)

        points.append(self.end.pos)

        render.draw_lines((237, 248, 100), False, points, width=0.05)

# A spring whose foce applied when compressed is proportional to the compressed distance
class HookesSpring(Spring):
    def __init__(self, stiffness: float = 10, **kwargs):
        super().__init__(**kwargs)
        self.stiffness = stiffness
    
    def magnitude(self, dist: float) -> float:
        return dist * self.stiffness

# A spring whose foce applied when compressed is quadratic to the compressed distance
class QuadraticSpring(Spring):
    def __init__(self, stiffness: float = 10, **kwargs):
        super().__init__(**kwargs)
        self.stiffness = stiffness

    def magnitude(self, dist: float) -> Tuple[Force, Force]:
        return dist ** 2 * self.stiffness

# A spring whose foce applied when compressed is constant
class ConstantSpring(Spring):
    def __init__(self, stiffness: float = 10, **kwargs):
        super().__init__(**kwargs)
        self.stiffness = stiffness

    def magnitude(self, _: float) -> Tuple[Force, Force]:
        return self.stiffness

# A spring whose foce applied when compressed is antiproportional to the compressed amount (with a maximum)
class HyperbolicSpring(Spring):
    def __init__(self, stiffness: float = 10, **kwargs):
        super().__init__(**kwargs)
        self.stiffness = stiffness
    
    def magnitude(self, dist: float) -> Tuple[Force, Force]:
        return self.stiffness / dist

class Simulation(threading.Thread):
    root_anchor: Anchor
    gravity: Force
    gravity_enabled: bool
    anchors: List[Anchor]
    springs: List[Spring]

    def __init__(self,  *args, **kwargs):
        super(Simulation, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()

        self.gravity_enabled = True
        self.gravity = Force((0, -9.81))
        self.root_anchor = Anchor((0, 0), static=True)
        self.anchors = [
            self.root_anchor,
            Anchor((0, -1), vel=(2, 0)),
            # Anchor((1, 0))
        ]
        self.springs = [
            HyperbolicSpring(stiffness=200, max_force=100, start=self.anchors[0], end=self.anchors[1]),
            # QuadraticSpring(stiffness=2, start=self.anchors[1], end=self.anchors[2]),
            # QuadraticSpring(stiffness=2, start=self.anchors[0], end=self.anchors[2]),
        ]
        self.records = []
    
    def toggle(self):
        if self._pause_event.is_set():
            self.resume()
        else:
            self.pause()

    def stop(self):
        self._stop_event.set()

    def pause(self):
        self._pause_event.set()

    def resume(self):
        self._pause_event.clear()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        while not self._stop_event.is_set():
            if not self._pause_event.is_set():
                self.update()
            time.sleep(SIM_TO_REAL * TIMESTEP)

    def update(self):
        for anchor in self.anchors[:]:
            if anchor.pos.magnitude_squared() > 2000:
                self.anchors.remove(anchor)
        # apply the forces from the springs
        for spring in self.springs:
            spring.apply()

        if self.gravity_enabled:
            # apply gravity
            for anchor in self.anchors:
                anchor.apply(self.gravity)
        
        # update positions
        for anchor in self.anchors:
            anchor.update()
