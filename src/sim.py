from typing import List, Tuple
from abc import ABC, abstractmethod
import pygame
import threading
import time

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
        self.coef = 0 if static else 1 / mass
    
    # Apply a force to this anchor
    # F = m * a
    def apply(self, force: Force):
        self.vel += TIMESTEP * self.coef * force.vec
    
    # Update the position of this anchor
    def update(self):
        self.pos += TIMESTEP * self.vel

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

# A spring whose foce applied when compressed is proportional to the compressed distance
class HookesSpring(Spring):
    def __init__(self, stiffness: float, start=Anchor((0, 0)), end=None):
        super().__init__(start, end)
        self.stiffness = stiffness
    
    # Returns the force this spring applies on start and end
    def force(self) -> Tuple[Force, Force]:
        return Force.pair((self.end.pos - self.start.pos) * self.stiffness)

# A spring whose foce applied when compressed is quadratic to the compressed distance
class QuadraticSpring(Spring):
    def __init__(self, stiffness: float, start=Anchor((0, 0)), end=None):
        super().__init__(start, end)
        self.stiffness = stiffness

    
    # Returns the force this spring applies on start and end
    def force(self) -> Tuple[Force, Force]:
        dir = (self.end.pos - self.start.pos)
        return Force.pair(dir.scale_to_length(dir.magnitude_squared()) * self.stiffness)


class Simulation(threading.Thread):
    root_anchor: Anchor
    anchors: List[Anchor]
    springs: List[Spring]

    def __init__(self,  *args, **kwargs):
        super(Simulation, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

        self.root_anchor = Anchor((0, 0), static=True)
        self.anchors = [self.root_anchor]
        self.springs = []
    
    def stop(self):
        self._stop_event.set()
        pygame.quit()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        while not self._stop_event.is_set():
            self.update()
            time.sleep(SIM_TO_REAL * TIMESTEP)

    def update(self):
        for spring in self.springs:
            spring.apply()
        
        for anchor in self.anchors:
            anchor.update()
