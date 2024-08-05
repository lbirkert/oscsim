import pygame
import os
from sim import Simulation, Anchor
from render import Render, Camera
from grid import render_grid
from ui import UI

sim = Simulation()
sim.start()

running = True
pygame.init()
screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
clock = pygame.time.Clock()

camera = Camera()
render = Render(screen, camera)
ui = UI(screen, sim)

records = []

drag_mouse_start = None
drag_camera_start = None
drag_anchor = None

imgs = {}

for name in os.listdir("imgs"):
    if not name.endswith(".png"):
        continue

    path = os.path.join("imgs", name)

    imgs[name[:-4]] = pygame.image.load(path)

try: 
    while running:
        time_delta = clock.tick(60) / 1000.0

        # process events sent by pygame
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    sim.toggle()
                    ui.toggle_show()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                anchor_rect = pygame.Rect((render.width - 64, render.height - 64), (64, 64))
                if anchor_rect.collidepoint(pos):
                    print("kekw")
                    drag_anchor = Anchor(static=True)
                    sim.anchors.append(drag_anchor)
                else:
                    drag_mouse_start = pygame.Vector2(pos)
                    drag_camera_start = camera.pos
            
            if event.type == pygame.MOUSEMOTION:
                now = pygame.Vector2(pygame.mouse.get_pos())
                if drag_anchor is not None:
                    drag_anchor.pos = render.untransform_point(now)
                    print(drag_anchor.pos)
                if drag_mouse_start is not None:
                    delta = render.untransform_delta(drag_mouse_start - now)
                    camera.pos = drag_camera_start + delta
                
            if event.type == pygame.MOUSEBUTTONUP:
                if drag_anchor is not None:
                    drag_anchor.static = False
                    drag_anchor.update_coef()
                    drag_anchor = None
                drag_mouse_start = None

            if event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    camera.zoom *= 1.1
                elif event.y < 0:
                    camera.zoom /= 1.1

            if event.type == pygame.VIDEORESIZE:
                ui.resize(screen)
                render.resize()
        
        screen.fill("black")

        render_grid(render)
        
        for spring in sim.springs:
            spring.render(render)

        for anchor in sim.anchors:
            anchor.render(render)

        records.append(sim.anchors[1].pos.copy())

        if len(records) > 2:
            recs = records[::-1]
            x_records = [(pos.x, i / 300) for (i, pos) in enumerate(recs)]
            y_records = [(i / 300, pos.y) for (i, pos) in enumerate(recs)]
            render.draw_lines((255, 0, 0), False, x_records)
            render.draw_vline((255, 0, 0), recs[0].x)
            render.draw_lines((0, 0, 255), False, y_records)
            render.draw_hline((0, 0, 255), recs[0].y)

        # add images

        i = 64
        for name in ["anchor", "constant", "proportional", "quadratic", "hyperbolic"]:
            screen.blit(imgs[name], pygame.Rect((render.width - i, render.height - 64), (64, 64)))
            i += 64
        
        ui.update(events)

        pygame.display.flip()
except KeyboardInterrupt:
    print("stopping...")

pygame.quit()
sim.stop()
