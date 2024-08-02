import pygame

class Camera:
    # world pos of camera
    pos: pygame.Vector2
    # zoom level
    zoom: float

    def __init__(self, pos=(0, 0), zoom=0.2):
        self.pos = pygame.Vector2(pos)
        self.zoom = zoom

    # transforms point into screen coords
    def transform_point(self, point: pygame.Vector2) -> pygame.Vector2:
        coord = self.zoom * (point - self.pos)
        coord.y *= -1 # invert y-coordinate
        return coord
    
    def transform_x(self, x: float) -> float:
        return self.zoom * (x - self.pos.x)
    
    def transform_y(self, y: float) -> float:
        return -self.zoom * (y - self.pos.y)
    
    def transform_size(self, size: float) -> float:
        return size * self.zoom
    
    def untransform_point(self, point: pygame.Vector2):
        point.y *= -1
        return point / self.zoom - self.pos
    
    def untransform_delta(self, delta: pygame.Vector2):
        delta.y *= -1
        return delta / self.zoom
    
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

    def draw_circle(self, color, center, radius, transform=True):
        if transform:
            center = self.transform_point(center)
            radius = self.transform_size(radius)

        pygame.draw.circle(self.screen, color, center, radius)
    
    def draw_lines(self, color, closed, points, width=1, transform=True):
        if len(points) < 2:
            return
        
        if not width.is_integer():
            width = int(self.transform_size(width))

        if transform:
            points = [self.transform_point(x) for x in points]

        pygame.draw.lines(self.screen, color, closed, points, width)

    def draw_line(self, color, start, end, width=1, transform=True):
        if not width.is_integer():
            width = int(self.transform_size(width))

        if transform:
            start = self.transform_point(start)
            end = self.transform_point(end)

        pygame.draw.line(self.screen, color, start, end, width)

    def draw_hline(self, color, y: float, width=1, transform=True):
        if not width.is_integer():
            width = int(self.transform_size(width))

        if transform:
            y = self.transform_y(y)

        pygame.draw.line(self.screen, color, (0, y), (self.width, y), width)
    
    def draw_vline(self, color, x: float, width=1, transform=True):
        if not width.is_integer():
            width = int(self.transform_size(width))

        if transform:
            x = self.transform_x(x)
        
        pygame.draw.line(self.screen, color, (x, 0), (x, self.height), width)

    def transform_point(self, point: pygame.Vector2) -> pygame.Vector2:
        return self.offset + self.pixels * self.camera.transform_point(point)
    
    def transform_x(self, x: float) -> float:
        return self.offset.x + self.pixels * self.camera.transform_x(x)
    
    def transform_y(self, y: float) -> float:
        return self.offset.y + self.pixels * self.camera.transform_y(y)
    
    def transform_size(self, size: float) -> float:
        return self.pixels * self.camera.transform_size(size)
    
    def resize(self):
        self.width, self.height = self.screen.get_size()
        self.pixels = min(self.width, self.height)
        self.offset = pygame.Vector2(self.width, self.height) / 2

    def get_padding(self):
        return self.width - self.pixels / 2, self.height - self.pixels / 2
    
    def untransform_point(self, point: pygame.Vector2):
        return self.offset - self.camera.untransform_point(point / self.pixels)
    
    def untransform_delta(self, delta: pygame.Vector2):
        return self.camera.untransform_delta(delta / self.pixels)