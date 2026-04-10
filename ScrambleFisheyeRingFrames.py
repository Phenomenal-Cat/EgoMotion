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
OUTPUT_PATH = "/Users/murphyap/Desktop/shuffled_frames/"

# -------------------------
# PREP
# -------------------------

random.seed(SEED)

scene = bpy.context.scene
seq = scene.sequence_editor.active_strip

if not seq or seq.type != 'IMAGE':
    raise RuntimeError("Active strip must be an Image Sequence")

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -------------------------
# POLAR GRID SETUP
# -------------------------

# Precompute random permutation maps for each ring
ring_slice_maps = {}
for r in range(RINGS):
    perm = list(range(SLICES))
    random.shuffle(perm)
    ring_slice_maps[r] = perm

# -------------------------
# ITERATE FRAMES
# -------------------------

slice_angle = 2 * math.pi / SLICES

for frame_idx in range(seq.frame_start, seq.frame_start + seq.frame_duration):
    # Map scene frame to strip element
    strip_frame = frame_idx - seq.frame_start
    strip_frame = min(strip_frame, len(seq.elements) - 1)
    img_path = os.path.join(seq.directory, seq.elements[strip_frame].filename)

    # Load image
    img = bpy.data.images.load(img_path)
    width, height = img.size
    cx, cy = width * 0.5, height * 0.5
    radius = min(cx, cy)

    src = np.array(img.pixels[:], dtype=np.float32).reshape((height, width, 4))
    dst = np.zeros_like(src)

    ring_thickness = radius / RINGS

    # -------------------------
    # PROCESS PIXELS (inverse mapping)
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

            # Source slice index
            src_slice_idx = ring_slice_maps[ring_idx][slice_idx]

            # Local polar offsets
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

    out_img = bpy.data.images.new(
        name=f"frame_{frame_idx:04d}",
        width=width,
        height=height,
        alpha=True
    )
    out_img.pixels = dst.flatten()
    out_file = os.path.join(OUTPUT_DIR, f"frame_{frame_idx:04d}.png")
    out_img.filepath_raw = out_file
    out_img.file_format = 'PNG'
    out_img.save()

    # Cleanup
    bpy.data.images.remove(img)
    bpy.data.images.remove(out_img)

    print(f"Processed frame {frame_idx}")

print("All frames processed.")
