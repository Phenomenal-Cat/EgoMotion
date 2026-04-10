

import bpy
import numpy as np
import math
import os

# -------------------------
# SETTINGS
# -------------------------

WIDTH = 1024
HEIGHT = 1024
OUTPUT_FILE = "/Users/murphyap/Documents/NIF_Stimuli/Checkerboard/fisheye_checkerTest.png"

NUM_RINGS = 8
NUM_SLICES = 16
FOV_DEGREES = 180  # Full fisheye
BLACK = (0.0,0.0,0.0,1.0)
WHITE = (1.0,1.0,1.0,1.0)

# -------------------------
# PREP
# -------------------------

cx, cy = WIDTH/2, HEIGHT/2
radius_max = min(cx, cy)
img_pixels = np.zeros((HEIGHT, WIDTH, 4), dtype=np.float32)

# FOV in radians
fov_rad = math.radians(FOV_DEGREES)
theta_max = fov_rad / 2  # half of fisheye FOV
delta_theta = theta_max / NUM_RINGS

# Equidistant projection: r = Rmax * theta / theta_max
theta_edges = np.linspace(0, theta_max, NUM_RINGS + 1)
r_edges = radius_max * (theta_edges / theta_max)

# Angular slice width
slice_angle = 2 * math.pi / NUM_SLICES

# -------------------------
# GENERATE CHECKERBOARD
# -------------------------

for y in range(HEIGHT):
    for x in range(WIDTH):
        dx = x + 0.5 - cx
        dy = y + 0.5 - cy
        r = math.hypot(dx, dy)
        if r > radius_max:
            img_pixels[y, x] = (0,0,0,0)
            continue

        # Determine ring index (equal angular width)
        ring_idx = np.searchsorted(r_edges, r, side='right') - 1
        ring_idx = np.clip(ring_idx, 0, NUM_RINGS-1)

        # Angular slice
        theta = math.atan2(dy, dx) % (2*math.pi)
        slice_idx = int(theta / slice_angle)

        # Checkerboard color
        color = WHITE if (ring_idx + slice_idx) % 2 == 0 else BLACK
        img_pixels[y, x] = color

# -------------------------
# SAVE IMAGE
# -------------------------

out_img = bpy.data.images.new(
    "fisheye_checker",
    width=WIDTH,
    height=HEIGHT,
    alpha=True
)
out_img.pixels = img_pixels.flatten()
out_img.filepath_raw = OUTPUT_FILE
out_img.file_format = 'PNG'
out_img.save()

print(f"Fisheye checkerboard saved to {OUTPUT_FILE}")
