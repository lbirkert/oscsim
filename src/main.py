import pygame
from sim import Simulation
from render import Render

simulation = Simulation()
simulation.start()

running = True
pygame.init()
screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
clock = pygame.time.Clock()
render = Render(screen)

try: 
    while running:
        # process events sent by pygame
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.VIDEORESIZE:
                render.resize()

        screen.fill("black")
        
        for spring in simulation.springs:
            spring.render(render)

        for anchor in simulation.anchors:
            anchor.render(render)

        pygame.display.flip()
        clock.tick(60)
except KeyboardInterrupt:
    print("stopping...")

pygame.quit()
simulation.stop()