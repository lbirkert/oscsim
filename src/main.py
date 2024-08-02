import pygame
from sim import Simulation

simulation = Simulation()
simulation.start()

running = True
pygame.init()
screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
clock = pygame.time.Clock()
width, height = screen.get_size()
    
while running:
    # process events sent by pygame
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.VIDEORESIZE:
            width, height = screen.get_size()

    screen.fill("black")
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
simulation.stop()