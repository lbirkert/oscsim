import pygame
import os
import time
from sim import Simulation, Anchor, ConstantSpring, HookesSpring, QuadraticSpring, HyperbolicSpring, Spring
from render import Render, Camera
from grid import render_grid
from ui import SettingsUI, AnchorUI, SpringUI

sim = Simulation()
sim.start()

running = True
pygame.init()
screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
clock = pygame.time.Clock()

camera = Camera()
render = Render(screen, camera)
settings_ui = SettingsUI(screen, sim)
entity_ui = None
ui_show = False

records = []
previous_selection = []

drag_mouse_start = None
drag_camera_start = None
drag_start = 0
drag_anchor = None

# (icon_name, string_constructor)
springs = [
    ("constant", ConstantSpring),
    ("proportional", HookesSpring),
    ("quadratic", QuadraticSpring),
    ("hyperbolic", HyperbolicSpring),
]

imgs = {}

for name in os.listdir("imgs"):
    if not name.endswith(".png"):
        continue

    path = os.path.join("imgs", name)

    imgs[name[:-4]] = pygame.image.load(path)

try: 
    while running:
        time_delta = clock.tick(60) / 1000.0
        selected = [x for x in sim.entities if x.selected]

        # process events sent by pygame
        events = pygame.event.get()
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        for event in events:
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    sim.toggle()
                    ui_show = not ui_show

                if event.key == pygame.K_BACKSPACE:
                    for entity in sim.entities[:]:
                        if entity.selected and entity in sim.entities:
                            sim.remove(entity)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                drag_start = time.time()

                # discard selection if shift is not pressed
                pressed = pygame.key.get_pressed()
                unselect = not pressed[pygame.K_LSHIFT] and not pressed[pygame.K_RSHIFT]

                # handle spring buttons
                i = 128
                for (_, spring) in springs:
                    rect = pygame.Rect((render.width - i, render.height - 64), (64, 64))
                    if rect.collidepoint(mouse_pos):
                        for i in range(len(selected) - 1):
                            spring = spring(start=selected[i], end=selected[i+1])
                            sim.springs.append(spring)
                            sim.entities.append(spring)
                        break

                    i += 64

                anchor_rect = pygame.Rect((render.width - 64, render.height - 64), (64, 64))
                if anchor_rect.collidepoint(mouse_pos):
                    if unselect:
                        sim.unselect()
                    drag_anchor = Anchor(lock=True)
                    drag_anchor.selected = True
                    sim.anchors.append(drag_anchor)
                    sim.entities.append(drag_anchor)

                for entity in sim.entities:
                    if entity.clicked(render, mouse_pos):
                        if unselect:
                            sim.unselect()
                        entity.selected = True
                        if isinstance(entity, Anchor):
                            entity.lock()
                            drag_anchor = entity
                        break

                if drag_anchor is None:
                    drag_mouse_start = mouse_pos
                    drag_camera_start = camera.pos
            
            if event.type == pygame.MOUSEMOTION:
                if drag_anchor is not None:
                    if not pygame.mouse.get_pressed()[0]:
                        drag_anchor = None
                    else:
                        drag_anchor.pos = render.untransform_point(mouse_pos)
                if drag_mouse_start is not None:
                    if not pygame.mouse.get_pressed()[0]:
                        drag_mouse_start = None
                    else:
                        delta = render.untransform_delta(drag_mouse_start - mouse_pos)
                        camera.pos = drag_camera_start + delta
                
            if event.type == pygame.MOUSEBUTTONUP:
                if drag_mouse_start is not None:
                    if (drag_mouse_start - mouse_pos).magnitude_squared() < 10:
                        # unselect everything
                        sim.unselect()
                    drag_mouse_start = None

                if drag_anchor is not None:
                    drag_anchor.unlock()
                    drag_anchor = None

            if event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    camera.zoom *= 1.1
                elif event.y < 0:
                    camera.zoom /= 1.1

            if event.type == pygame.VIDEORESIZE:
                settings_ui.resize(screen)
                if entity_ui is not None:
                    entity_ui.resize(screen)
                render.resize()
        
        screen.fill("black")

        render_grid(render)
        
        for spring in sim.springs:
            spring.render(render)

        for anchor in sim.anchors:
            anchor.render(render)
        
        if len(selected) > 0 and isinstance(selected[0], Anchor):
            anchor = selected[0]
            records.append(anchor.pos.copy())

            if len(records) > 200:
                records.pop(0)

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
        icons = ["anchor"]
        icons.extend([x for (x, _) in springs])
        for name in icons:
            screen.blit(imgs[name], pygame.Rect((render.width - i, render.height - 64), (64, 64)))
            i += 64
            
        if selected != previous_selection:
            if len(selected) == 1:
                if isinstance(selected[0], Anchor):
                    entity_ui = AnchorUI(selected[0])
                elif isinstance(selected[0], Spring):
                    entity_ui = SpringUI(selected[0])
                entity_ui.resize(screen)

            if len(selected) != 1:
                entity_ui = None
            previous_selection = selected

        
        # hide UI when moving mouse
        if ui_show and (drag_anchor is None and \
            (drag_mouse_start is None or \
                (drag_mouse_start - mouse_pos).magnitude_squared() < 10)):
            settings_ui.update(events)
            if entity_ui is not None:
                entity_ui.update(events)



        pygame.display.flip()
except KeyboardInterrupt:
    print("stopping...")

pygame.quit()
sim.stop()
