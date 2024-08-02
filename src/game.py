import pygame
import threading

stop_event = threading.Event

class Game(threading.Thread):
    def __init__(self,  *args, **kwargs):
        super(Game, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()
        pygame.quit()

    def stopped(self):
        return self._stop_event.is_set()
    
    def run(self):
        self.setup()
        while not self.stopped():
            self.render()
            
            pygame.display.flip()
            self.clock.tick(60)

    def setup(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1280, 720))
        self.clock = pygame.time.Clock()
    
    def render(self):
        # process events sent by pygame
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stop()

        self.screen.fill("black")