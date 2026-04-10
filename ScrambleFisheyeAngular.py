import bpy
import numpy as np
import math
import random
import os

# -------------------------
# SETTINGS
# -------------------------

RINGS = 8
SLICES = 24            # controls angular quantization
SEED = 42
OUTPUT_PATH = "/Users/murphyap/Desktop/shuffled_frame_angular.png"

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
# ANGULAR OFFSETS PER RING
# -------------------------

# Offset in slice units, converted later to radians
ring_offsets = {
    r: random.randint(0, SLICES - 1)
    for r in range(RINGS)
}

slice_angle = 2 * math.pi / SLICES

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

        # Determine ring
        r_idx = min(int((r / radius) * RINGS), RINGS - 1)

        # Quantize angle to slice
        a_idx = int(theta / slice_angle)

        # Apply angular offset
        new_a_idx = (a_idx + ring_offsets[r_idx]) % SLICES
        new_theta = new_a_idx * slice_angle + (theta % slice_angle)

        # Back to cartesian
        nx = int(round(cx + r * math.cos(new_theta)))
        ny = int(round(cy + r * math.sin(new_theta)))

        if 0 <= nx < width and 0 <= ny < height:
            out_pixels[ny, nx] = pixels[y, x]

# -------------------------
# SAVE RESULT
# -------------------------

out = bpy.data.images.new(
    name="angular_shuffle",
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

print("Angular-only polar shuffle complete.")
