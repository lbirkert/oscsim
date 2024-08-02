from typing import Tuple
import pygame

TIMESTEP = 0.01

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

class HookesSpring:
    def __init__(self, stiffness: float, start=Anchor((0, 0)), end=None):
        self.stiffness = stiffness

        self.start = start
        self.end = end if end is not None else start
    
    # Returns the force this spring applies on start and end
    def force(self) -> Tuple[Force, Force]:
        return Force.pair((self.end.pos - self.start.pos) * self.stiffness)