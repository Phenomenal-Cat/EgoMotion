# ScrambleFisheye.py


import bpy
import numpy as np
import math
import random
import os

# -------------------------
# USER SETTINGS
# -------------------------

MOVIE_PATH = "/Volumes/NIFVAULT/projects/murphyap_NIF/NIF_Stimuli/Dome Content/Lucid_Concat.mp4"
OUTPUT_DIR = "/Volumes/NIFVAULT/projects/murphyap_NIF/NIF_Stimuli/Dome Content/Lucid_Scrambled/"

RINGS = 8              # radial divisions
SLICES = 24            # angular divisions
SEED = 42              # for repeatable shuffling
FRAME_START = 1
FRAME_END = None       # None = full movie

# -------------------------
# SETUP
# -------------------------

random.seed(SEED)
os.makedirs(OUTPUT_DIR, exist_ok=True)

clip = bpy.data.movieclips.load(MOVIE_PATH)
scene = bpy.context.scene

width = clip.size[0]
height = clip.size[1]

cx = width // 2
cy = height // 2
radius = min(cx, cy)

if FRAME_END is None:
    FRAME_END = clip.frame_duration

# -------------------------
# HELPER FUNCTIONS
# -------------------------

def polar_index(x, y):
    dx = x - cx
    dy = y - cy
    r = math.sqrt(dx * dx + dy * dy)
    theta = math.atan2(dy, dx) % (2 * math.pi)
    return r, theta

# -------------------------
# MAIN LOOP
# -------------------------

for frame in range(FRAME_START, FRAME_END + 1):
    print(f"Processing frame {frame}")

    clip.frame_offset = frame
    clip.reload()

    # Get pixel data (RGBA flat array)
    pixels = np.array(clip.pixels[:], dtype=np.float32)
    pixels = pixels.reshape((height, width, 4))

    # Create segment buffers
    segments = {}
    for r in range(RINGS):
        for a in range(SLICES):
            segments[(r, a)] = []

    # Assign pixels to polar segments
    for y in range(height):
        for x in range(width):
            r, theta = polar_index(x, y)

            if r > radius:
                continue

            r_idx = int((r / radius) * RINGS)
            a_idx = int((theta / (2 * math.pi)) * SLICES)

            r_idx = min(r_idx, RINGS - 1)
            a_idx = min(a_idx, SLICES - 1)

            segments[(r_idx, a_idx)].append((y, x))

    # Shuffle segment destinations
    keys = list(segments.keys())
    shuffled_keys = keys[:]
    random.shuffle(shuffled_keys)

    out_pixels = np.zeros_like(pixels)

    for src_key, dst_key in zip(keys, shuffled_keys):
        src_pixels = segments[src_key]
        dst_pixels = segments[dst_key]

        count = min(len(src_pixels), len(dst_pixels))
        for i in range(count):
            sy, sx = src_pixels[i]
            dy, dx = dst_pixels[i]
            out_pixels[dy, dx] = pixels[sy, sx]

    # Write image
    img = bpy.data.images.new(
        name=f"frame_{frame:04d}",
        width=width,
        height=height,
        alpha=True
    )

    img.pixels = out_pixels.flatten()
    img.filepath_raw = os.path.join(OUTPUT_DIR, f"frame_{frame:04d}.png")
    img.file_format = 'PNG'
    img.save()

    bpy.data.images.remove(img)

print("Done.")
