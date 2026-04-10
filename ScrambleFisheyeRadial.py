import bpy
import numpy as np
import math
import random
import os

# -------------------------
# SETTINGS
# -------------------------

RINGS = 8
SLICES = 24
SEED = 42
OUTPUT_PATH = "/Users/murphyap/Desktop/shuffled_frame_radial.png"

random.seed(SEED)

scene = bpy.context.scene
frame = scene.frame_current
seq = scene.sequence_editor.active_strip

if not seq or seq.type != 'IMAGE':
    raise RuntimeError("Active strip must be an Image Sequence")

# -------------------------
# RESOLVE IMAGE
# -------------------------

strip_frame = max(0, frame - seq.frame_start)
strip_frame = min(strip_frame, len(seq.elements) - 1)

img_path = os.path.join(seq.directory, seq.elements[strip_frame].filename)
img = bpy.data.images.load(img_path)

width, height = img.size
cx, cy = width // 2, height // 2
radius = min(cx, cy)

pixels = np.array(img.pixels[:], dtype=np.float32)
pixels = pixels.reshape((height, width, 4))

out_pixels = np.zeros_like(pixels)

# -------------------------
# RADIAL OFFSETS PER SLICE
# -------------------------

# For each angular slice, generate a shuffled ring order
slice_ring_maps = {}

for a in range(SLICES):
    rings = list(range(RINGS))
    random.shuffle(rings)
    slice_ring_maps[a] = rings

slice_angle = 2 * math.pi / SLICES
ring_thickness = radius / RINGS

# -------------------------
# PROCESS PIXELS
# -------------------------

for y in range(height):
    for x in range(width):
        dx = x - cx
        dy = y - cy
        r = math.sqrt(dx * dx + dy * dy)

        if r > radius:
            continue

        theta = math.atan2(dy, dx) % (2 * math.pi)

        # Angular slice
        a_idx = int(theta / slice_angle)
        a_idx = min(a_idx, SLICES - 1)

        # Radial ring
        r_idx = int(r / ring_thickness)
        r_idx = min(r_idx, RINGS - 1)

        # Radial offset within ring
        r_inner = r_idx * ring_thickness
        r_offset = r - r_inner

        # Shuffled ring destination
        new_r_idx = slice_ring_maps[a_idx][r_idx]
        new_r = new_r_idx * ring_thickness + r_offset

        # Back to cartesian
        nx = int(round(cx + new_r * math.cos(theta)))
        ny = int(round(cy + new_r * math.sin(theta)))

        if 0 <= nx < width and 0 <= ny < height:
            out_pixels[ny, nx] = pixels[y, x]

# -------------------------
# SAVE RESULT
# -------------------------

out = bpy.data.images.new(
    name="radial_shuffle",
    width=width,
    height=height,
    alpha=True
)

out.pixels = out_pixels.flatten()
out.filepath_raw = OUTPUT_PATH
out.file_format = 'PNG'
out.save()

bpy.data.images.remove(img)
bpy.data.images.remove(out)

print("Radial-only polar shuffle complete.")
