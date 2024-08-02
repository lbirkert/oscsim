import math
from render import Render

def render_grid(render: Render):
    # TODO: make this dynamic
    GRID_SIZE = 0.004 / (10 ** math.floor(math.log10(render.camera.zoom)))
    COLORS = [
        (20, 20, 20),
        (40, 40, 40),
        (60, 60, 60),
        (100, 100, 100),
    ]
    pad_x, pad_y = render.get_padding()
    grid_off_x = math.floor(render.camera.pos.x / GRID_SIZE)
    grid_off_y = math.floor(render.camera.pos.y / GRID_SIZE)
    grid_n_x = int(((2 * pad_x / render.width) + 1) / (render.camera.zoom * GRID_SIZE))
    grid_n_y = int(((2 * pad_y / render.height) + 1) / (render.camera.zoom * GRID_SIZE))
    grid_x = [grid_off_x + (i - int(grid_n_x / 2)) for i in range(grid_n_x)]
    grid_y = [grid_off_y + (i - int(grid_n_y / 2)) for i in range(grid_n_y)]

    for x in grid_x:
        render.draw_vline(COLORS[0], x * GRID_SIZE)
    for y in grid_y:
        render.draw_hline(COLORS[0], y * GRID_SIZE)

    for x in grid_x:
        if x % 10 == 0:
            render.draw_vline(COLORS[1], x * GRID_SIZE)
    for y in grid_y:
        if y % 10 == 0:
            render.draw_hline(COLORS[1], y * GRID_SIZE)

    for x in grid_x:
        if x % 100 == 0:
            render.draw_vline(COLORS[2], x * GRID_SIZE)
    for y in grid_y:
        if y % 100 == 0:
            render.draw_hline(COLORS[2], y * GRID_SIZE)
    
    for x in grid_x:
        if x % 1000 == 0:
            render.draw_vline(COLORS[3], x * GRID_SIZE)
    for y in grid_y:
        if y % 1000 == 0:
            render.draw_hline(COLORS[3], y * GRID_SIZE)

