import pygame
from sim import Simulation
from render import Render

simulation = Simulation()
simulation.start()

running = True
pygame.init()
screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
clock = pygame.time.Clock()
width, height = screen.get_size()
render = Render(screen)
    
while running:
    # process events sent by pygame
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.VIDEORESIZE:
            width, height = screen.get_size()

    screen.fill("black")

    for anchor in simulation.anchors:
        anchor.render(render)

    for spring in simulation.springs:
        spring.render(render)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
simulation.stop()