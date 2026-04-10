import bpy
import random
import math

# ================= USER SETTINGS =================

IMAGE_NAME = "Voronoi_Tile_Displacement"
IMAGE_WIDTH = 1024
IMAGE_HEIGHT = 1024

GRID_X = 10
GRID_Y = 10
JITTER_AMOUNT = 0.35     # 0.0 = perfect grid

CRACK_WIDTH = 0.03      # Controls gap size between tiles
EDGE_SOFTNESS = 0.01    # Feathering of tile edges

TILE_HEIGHT = 1.0       # White value
CRACK_HEIGHT = 0.0      # Black value

SEED = 42

# ================================================


def generate_jittered_grid(grid_x, grid_y, jitter):
    random.seed(SEED)
    points = []

    for y in range(grid_y):
        for x in range(grid_x):
            px = (x + 0.5) / grid_x
            py = (y + 0.5) / grid_y

            px += (random.random() - 0.5) * jitter / grid_x
            py += (random.random() - 0.5) * jitter / grid_y

            points.append((px % 1.0, py % 1.0))

    return points


def torus_distance(u, v, px, py):
    dx = abs(u - px)
    dy = abs(v - py)

    dx = min(dx, 1.0 - dx)
    dy = min(dy, 1.0 - dy)

    return math.sqrt(dx * dx + dy * dy)


def smoothstep(edge0, edge1, x):
    t = max(0.0, min(1.0, (x - edge0) / (edge1 - edge0)))
    return t * t * (3.0 - 2.0 * t)


def generate_displacement_map():
    image = bpy.data.images.new(
        IMAGE_NAME,
        width=IMAGE_WIDTH,
        height=IMAGE_HEIGHT,
        alpha=False,
        float_buffer=False
    )

    pixels = [0.0] * (IMAGE_WIDTH * IMAGE_HEIGHT * 4)

    points = generate_jittered_grid(GRID_X, GRID_Y, JITTER_AMOUNT)

    for y in range(IMAGE_HEIGHT):
        v = y / IMAGE_HEIGHT
        for x in range(IMAGE_WIDTH):
            u = x / IMAGE_WIDTH

            f1 = float("inf")
            f2 = float("inf")

            for px, py in points:
                d = torus_distance(u, v, px, py)

                if d < f1:
                    f2 = f1
                    f1 = d
                elif d < f2:
                    f2 = d

            # Distance to Voronoi edge
            edge_dist = f2 - f1

            # Shrink cell to create cracks
            interior = smoothstep(CRACK_WIDTH, CRACK_WIDTH + EDGE_SOFTNESS, edge_dist)

            # Height mapping
            height = (
                CRACK_HEIGHT * (1.0 - interior) +
                TILE_HEIGHT * interior
            )

            idx = (y * IMAGE_WIDTH + x) * 4
            pixels[idx]     = height
            pixels[idx + 1] = height
            pixels[idx + 2] = height
            pixels[idx + 3] = 1.0

    image.pixels = pixels
    image.pack()
    return image


# ================= EXECUTION =================

img = generate_displacement_map()
print(f"Voronoi tile displacement map '{img.name}' generated successfully.")
