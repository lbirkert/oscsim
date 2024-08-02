import pygame

class Camera:
    # world pos of camera
    pos: pygame.Vector2
    # zoom level
    zoom: float

    def __init__(self, pos=(0, 0), zoom=0.05):
        self.pos = pygame.Vector2(pos)
        self.zoom = zoom

    # transforms point into screen coords
    def transform_point(self, point: pygame.Vector2) -> pygame.Vector2:
        coord = self.zoom * (point - self.pos)
        coord.y *= -1 # invert y-coordinate
        return coord
    
    def transform_size(self, size: float) -> float:
        return size * self.zoom

class Render:
    camera: Camera
    screen: pygame.Surface
    width: float
    height: float
    # min(width, height)
    pixels: float
    # ((width - pixels) / 2, (height - pixels) / 2)
    offset: pygame.Vector2

    def __init__(self, screen: pygame.Surface, camera = Camera()):
        self.screen = screen
        self.camera = camera
        self.resize()

    def draw_circle(self, color, center, radius):
        pygame.draw.circle(self.screen, color,
                           self.transform_point(center), self.transform_size(radius))
    
    def draw_lines(self, color, closed, points, width=1):
        points = [self.transform_point(x) for x in points]
        pygame.draw.lines(self.screen, color, closed, points, int(self.transform_size(width)))

    def draw_line(self, color, start, end, width=1):
        pygame.draw.line(self.screen, color, start, end, int(self.transform_size(width)))

    def transform_point(self, point: pygame.Vector2) -> pygame.Vector2:
        return self.offset + self.pixels * self.camera.transform_point(point)
    
    def transform_size(self, size: float) -> float:
        return self.pixels * self.camera.transform_size(size)
    
    def resize(self):
        self.width, self.height = self.screen.get_size()
        self.pixels = min(self.width, self.height)
        self.offset = pygame.Vector2(self.width, self.height) / 2