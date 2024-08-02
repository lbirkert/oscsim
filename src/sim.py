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
    def __init__(self, pos=(0,0), vel=(0,0), static=False, mass=1):
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(vel)
        self.static = static
        # in kilograms
        self.mass = mass
        self.coef = 0 if static else 1 / mass
    
    # Apply a force to this anchor
    # F = m * a
    def apply(self, force: Force):
        self.vel += TIMESTEP * self.coef * force.vec
    
    # Update the position of this anchor
    def update(self):
        self.pos += TIMESTEP * self.vel

    def render(self, render: Render):
        SIZE_RATIO = 0.10876
        radius = math.sqrt(self.mass) * SIZE_RATIO
        color = (100, 100, 100) if self.static else (255, 255, 255)
        render.draw_circle(color, self.pos, radius)

class Spring(ABC):
    start: Anchor
    end: Anchor

    def __init__(self, **kwargs):
        self.start = kwargs.get("start", Anchor((0, 0)))
        self.end = kwargs.get("end", Anchor(self.start.pos))

        assert isinstance(self.start, Anchor)
        assert isinstance(self.end, Anchor)

    @abstractmethod
    def force(self) -> Tuple[Force, Force]:
        pass

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

        render.draw_lines((100, 100, 0), False, points, width=0.05)

# A spring whose foce applied when compressed is proportional to the compressed distance
class HookesSpring(Spring):
    def __init__(self, stiffness: float, **kwargs):
        super().__init__(**kwargs)
        self.stiffness = stiffness
    
    # Returns the force this spring applies on start and end
    def force(self) -> Tuple[Force, Force]:
        return Force.pair((self.end.pos - self.start.pos) * self.stiffness)

# A spring whose foce applied when compressed is quadratic to the compressed distance
class QuadraticSpring(Spring):
    def __init__(self, stiffness: float, **kwargs):
        super().__init__(**kwargs)
        self.stiffness = stiffness

    
    # Returns the force this spring applies on start and end
    def force(self) -> Tuple[Force, Force]:
        delta = (self.end.pos - self.start.pos)
        dist = delta.magnitude()
        if dist == 0:
            return Force.pair((0, 0))
        return Force.pair(delta * dist * self.stiffness)


class Simulation(threading.Thread):
    root_anchor: Anchor
    gravity: Force
    anchors: List[Anchor]
    springs: List[Spring]

    def __init__(self,  *args, **kwargs):
        super(Simulation, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

        self.gravity = Force((0, -9.81))
        self.root_anchor = Anchor((0, 0), static=True)
        self.anchors = [
            self.root_anchor,
            Anchor((0, -1), vel=(0, 0)),
            Anchor((1, 0))
        ]
        self.springs = [
            HookesSpring(stiffness=8, start=self.anchors[0], end=self.anchors[1]),
            QuadraticSpring(stiffness=2, start=self.anchors[1], end=self.anchors[2]),
            QuadraticSpring(stiffness=2, start=self.anchors[0], end=self.anchors[2]),
        ]
        self.records = []
    
    def stop(self):
        self._stop_event.set()
        pygame.quit()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        i = 0
        while not self._stop_event.is_set():
            self.update()
            time.sleep(SIM_TO_REAL * TIMESTEP)
            i += 1

    def update(self):
        # apply the forces from the springs
        for spring in self.springs:
            spring.apply()

        # apply gravity
        for anchor in self.anchors:
            anchor.apply(self.gravity)
        
        # update positions
        for anchor in self.anchors:
            anchor.update()