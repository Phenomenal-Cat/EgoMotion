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
OUTPUT_PATH = "/Desktop/shuffled_frame.png"

random.seed(SEED)

scene = bpy.context.scene
frame = scene.frame_current
seq = scene.sequence_editor.active_strip

if not seq or seq.type != 'IMAGE':
    raise RuntimeError("Active strip must be an Image Sequence")

# -------------------------
# RESOLVE IMAGE FOR FRAME
# -------------------------

# Frame index inside the strip
strip_frame = frame - seq.frame_start
strip_frame = max(0, strip_frame)

# Clamp to available images
strip_frame = min(strip_frame, len(seq.elements) - 1)

img_path = os.path.join(
    seq.directory,
    seq.elements[strip_frame].filename
)

img = bpy.data.images.load(img_path)
width, height = img.size

cx, cy = width // 2, height // 2
radius = min(cx, cy)

# -------------------------
# HELPERS
# -------------------------

def polar_index(x, y):
    dx = x - cx
    dy = y - cy
    r = math.sqrt(dx * dx + dy * dy)
    theta = math.atan2(dy, dx) % (2 * math.pi)
    return r, theta

# -------------------------
# PROCESS IMAGE
# -------------------------

pixels = np.array(img.pixels[:], dtype=np.float32)
pixels = pixels.reshape((height, width, 4))

segments = {(r, a): [] for r in range(RINGS) for a in range(SLICES)}

for y in range(height):
    for x in range(width):
        r, theta = polar_index(x, y)
        if r > radius:
            continue

        r_idx = min(int((r / radius) * RINGS), RINGS - 1)
        a_idx = min(int((theta / (2 * math.pi)) * SLICES), SLICES - 1)

        segments[(r_idx, a_idx)].append((y, x))

keys = list(segments.keys())
shuffled = keys[:]
random.shuffle(shuffled)

out_pixels = np.zeros_like(pixels)

for src, dst in zip(keys, shuffled):
    src_pts = segments[src]
    dst_pts = segments[dst]
    count = min(len(src_pts), len(dst_pts))

    for i in range(count):
        sy, sx = src_pts[i]
        dy, dx = dst_pts[i]
        out_pixels[dy, dx] = pixels[sy, sx]

# -------------------------
# SAVE RESULT
# -------------------------

out = bpy.data.images.new(
    name="polar_shuffled",
    width=width,
    height=height,
    alpha=True
)

out.pixels = out_pixels.flatten()
out.filepath_raw = OUTPUT_PATH
out.file_format = 'PNG'
out.save()

# Cleanup
bpy.data.images.remove(img)
bpy.data.images.remove(out)

print("Polar shuffle complete for current VSE frame.")
