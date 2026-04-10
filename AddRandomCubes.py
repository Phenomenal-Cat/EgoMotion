# Add an array of randomized objects to scene

import bpy
import random
import math
import colorsys


def random_color():
	h = random.random() 		 # hue
	s = random.uniform(0.6, 1.0) # saturation
	v = random.uniform(0.6, 1.0) # brightness
	r, g, b = colorsys.hsv_to_rgb(h, s, v)
	return (r, g, b, 1)

#======= Delete any existign cube objects
for obj in bpy.context.scene.objects:
	if obj.type == 'MESH' and obj.name.startswith("Cube"):
		bpy.data.objects.remove(obj, do_unlink=True)

# -------- SETTINGS --------
COUNT = 500

# Location range

X_RANGE = (-100, 100)
Y_RANGE = (-100, 100)
Z_RANGE = (0, 50)

# Scale range
SCALE_MIN = 0.2
SCALE_MAX = 3.0

# Rotation range (radians)
ROT_MIN = 0
ROT_MAX = 2 * math.pi
# --------------------------

for i in range(COUNT):
	# Random location
	x = random.uniform(*X_RANGE)
	y = random.uniform(*Y_RANGE)
	z = random.uniform(*Z_RANGE)

	# Create cube
	bpy.ops.mesh.primitive_cube_add(location=(x, y, z))
	cube = bpy.context.object

	# Random scale
	s = random.uniform(SCALE_MIN, SCALE_MAX)
	cube.scale = (s, s, s)

	# Random rotation
	cube.rotation_euler = (
		random.uniform(ROT_MIN, ROT_MAX),
		random.uniform(ROT_MIN, ROT_MAX),
		random.uniform(ROT_MIN, ROT_MAX)
	)
	

# Apply random color to each cube
for obj in bpy.context.scene.objects:
	if obj.type == 'MESH' and obj.name.startswith("Cube"):
		mat = bpy.data.materials.new(name="RandomMat")
		mat.use_nodes = True
		bsdf = mat.node_tree.nodes["Principled BSDF"]
		bsdf.inputs["Base Color"].default_value = random_color()

		obj.data.materials.clear()
		obj.data.materials.append(mat)
		
		
#====== Apply continuous rotation to all cubes
for obj in bpy.context.scene.objects:
	if obj.type == 'MESH' and obj.name.startswith("Cube"):
		
		for i in range(3):  # X, Y, Z axes
			speed = random.uniform(0.02, 0.08)

			driver = obj.driver_add("rotation_euler", i).driver
			driver.type = 'SCRIPTED'

			var = driver.variables.new()
			var.name = "frame"
			var.targets[0].id_type = 'SCENE'
			var.targets[0].id = bpy.context.scene
			var.targets[0].data_path = "frame_current"

			driver.expression = f"frame * {speed}"