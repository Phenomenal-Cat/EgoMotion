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
OUTPUT_PATH = "/Users/murphyap/Desktop/shuffled_frame_ring.png"

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
cx, cy = width * 0.5, height * 0.5
radius = min(cx, cy)

src = np.array(img.pixels[:], dtype=np.float32)
src = src.reshape((height, width, 4))

dst = np.zeros_like(src)

# -------------------------
# POLAR GRID SETUP
# -------------------------

ring_thickness = radius / RINGS
slice_angle = 2 * math.pi / SLICES

# For each ring: destination slice -> source slice
ring_slice_maps = {}

for r in range(RINGS):
    perm = list(range(SLICES))
    random.shuffle(perm)
    ring_slice_maps[r] = perm

# -------------------------
# PROCESS (INVERSE MAPPING)
# -------------------------

for y in range(height):
    for x in range(width):
        dx = x + 0.5 - cx
        dy = y + 0.5 - cy
        r = math.hypot(dx, dy)

        if r > radius:
            continue

        theta = math.atan2(dy, dx) % (2 * math.pi)

        # Destination ring & slice
        ring_idx = min(int(r / ring_thickness), RINGS - 1)
        slice_idx = min(int(theta / slice_angle), SLICES - 1)

        # Which source slice maps here?
        src_slice_idx = ring_slice_maps[ring_idx][slice_idx]

        # Local coordinates inside the segment
        r_inner = ring_idx * ring_thickness
        r_offset = r - r_inner
        theta_offset = theta - slice_idx * slice_angle

        # Source polar coordinates
        src_theta = src_slice_idx * slice_angle + theta_offset
        src_r = r_inner + r_offset

        # Back to cartesian
        sx = int(cx + src_r * math.cos(src_theta))
        sy = int(cy + src_r * math.sin(src_theta))

        if 0 <= sx < width and 0 <= sy < height:
            dst[y, x] = src[sy, sx]

# -------------------------
# SAVE RESULT
# -------------------------

out = bpy.data.images.new(
    name="ring_segment_shuffle",
    width=width,
    height=height,
    alpha=True
)

out.pixels = dst.flatten()
out.filepath_raw = OUTPUT_PATH
out.file_format = 'PNG'
out.save()

bpy.data.images.remove(img)
bpy.data.images.remove(out)

print("Ring-wise polar segment shuffle complete.")
