# GaitPath.py

import bpy
import math

# साफ scene (optional: comment out if you don’t want to delete everything)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# -----------------------------
# Create camera + rig
# -----------------------------
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 1.7))
rig = bpy.context.object
rig.name = "Camera_Rig"

bpy.ops.object.camera_add(location=(0, 0, 0))
cam = bpy.context.object
cam.name = "Camera"

# Parent camera to rig
cam.parent = rig

# Set camera as active
bpy.context.scene.camera = cam

# -----------------------------
# Animate forward motion
# -----------------------------
rig.location = (0, 0, 1.7)
rig.keyframe_insert(data_path="location", frame=1)

rig.location = (0, 10, 1.7)
rig.keyframe_insert(data_path="location", frame=250)

# Linear interpolation
for fcurve in rig.animation_data.action.fcurves:
    for kp in fcurve.keyframe_points:
        kp.interpolation = 'LINEAR'

# -----------------------------
# Add head-bob driver (Z axis)
# -----------------------------
fcurve_z = rig.driver_add("location", 2)  # Z axis
driver_z = fcurve_z.driver
driver_z.type = 'SCRIPTED'

# Add frame variable
var = driver_z.variables.new()
var.name = "f"
var.targets[0].id_type = 'SCENE'
var.targets[0].id = bpy.context.scene
var.targets[0].data_path = "frame_current"

# Expression (realistic gait)
driver_z.expression = (
    "(0.04*sin(f*0.12))"
    "+ (0.015*sin(f*0.24 + 1.2))"
    "+ (-0.008*abs(sin(f*0.12)))"
) 

# -----------------------------
# Add lateral sway (X axis)
# -----------------------------
fcurve_x = rig.driver_add("location", 0)  # X axis
driver_x = fcurve_x.driver
driver_x.type = 'SCRIPTED'

var_x = driver_x.variables.new()s
var_x.name = "f"
var_x.targets[0].id_type = 'SCENE'
var_x.targets[0].id = bpy.context.scene
var_x.targets[0].data_path = "frame_current"

driver_x.expression = "0.02*sin(f*0.12 + 1.57)"

# -----------------------------
# Optional: slight rotation (roll)
# -----------------------------
fcurve_rot = rig.driver_add("rotation_euler", 2)  # Z rotation
driver_rot = fcurve_rot.driver
driver_rot.type = 'SCRIPTED'

var_r = driver_rot.variables.new()
var_r.name = "f"
var_r.targets[0].id_type = 'SCENE'
var_r.targets[0].id = bpy.context.scene
var_r.targets[0].data_path = "frame_current"

driver_rot.expression = "0.01*sin(f*0.12 + 1.57)"

# -----------------------------
# Camera tilt (subtle pitch)
# -----------------------------
fcurve_pitch = cam.driver_add("rotation_euler", 0)
driver_pitch = fcurve_pitch.driver
driver_pitch.type = 'SCRIPTED'

var_p = driver_pitch.variables.new()
var_p.name = "f"
var_p.targets[0].id_type = 'SCENE'
var_p.targets[0].id = bpy.context.scene
var_p.targets[0].data_path = "frame_current"

driver_pitch.expression = "0.015*sin(f*0.12)"

print("Camera walk cycle rig created!")