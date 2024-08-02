import pygame
from sim import Simulation
from render import Render, Camera
from grid import render_grid

simulation = Simulation()
simulation.start()

running = True
pygame.init()
screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
clock = pygame.time.Clock()
camera = Camera()
render = Render(screen, camera)

records = []

drag_mouse_start = None
drag_camera_start = None

try: 
    while running:
        # process events sent by pygame
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                drag_mouse_start = pygame.Vector2(pygame.mouse.get_pos())
                drag_camera_start = camera.pos
            
            if drag_mouse_start is not None and event.type == pygame.MOUSEMOTION:
                now = pygame.Vector2(pygame.mouse.get_pos())
                delta = render.untransform_delta(drag_mouse_start - now)
                camera.pos = drag_camera_start + delta
                
            if event.type == pygame.MOUSEBUTTONUP:
                drag_mouse_start = None

            if event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    camera.zoom *= 1.1
                elif event.y < 0:
                    camera.zoom /= 1.1

            if event.type == pygame.VIDEORESIZE:
                render.resize()

        screen.fill("black")

        render_grid(render)
        
        for spring in simulation.springs:
            spring.render(render)

        for anchor in simulation.anchors:
            anchor.render(render)

        records.append(simulation.anchors[1].pos.copy())

        if len(records) > 2:
            recs = records[::-1]
            x_records = [(pos.x, i / 300) for (i, pos) in enumerate(recs)]
            y_records = [(i / 300, pos.y) for (i, pos) in enumerate(recs)]
            render.draw_lines((255, 0, 0), False, x_records)
            render.draw_vline((255, 0, 0), recs[0].x)
            render.draw_lines((0, 0, 255), False, y_records)
            render.draw_hline((0, 0, 255), recs[0].y)

        pygame.display.flip()
        clock.tick(60)
except KeyboardInterrupt:
    print("stopping...")

pygame.quit()
simulation.stop()