import pygame

class Camera:
    # world pos of camera
    pos: pygame.Vector2
    # zoom level
    zoom: float

    def __init__(self, pos=(0, 0), zoom=0.01):
        self.pos = pygame.Vector2(pos)
        self.zoom = zoom

    # transforms point into screen coords
    def transform_point(self, point: pygame.Vector2) -> pygame.Vector2:
        return self.zoom * (point - self.pos)
    
    def transform_size(self, size: float) -> float:
        return float * self.zoom



class Renderer:
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


    def draw_circle(self, center, radius):
        pygame.draw.circle(self.screen, (255, 0, 0),
                           self.transform_point(center), self.transform_size(radius))

    def transform_point(self, point: pygame.Vector2) -> pygame.Vector2:
        self.transform_pixels(self.camera.transform_point(point))
    
    def transform_size(self, size: float) -> float:
        self.transform_pixels(self.camera.transform_size(size))
    
    def transform_pixels(self, screen_coords):
        self.offset + screen_coords * self.pixels
    
    def resize(self):
        self.width, self.height = self.screen.get_size()
        self.pixels = min(self.width, self.height)
        self.offset = pygame.Vector2(self.width - self.pixels, self.height - self.pixels) / 2