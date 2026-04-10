import bpy
import math

# -----------------------------
# SETTINGS
# -----------------------------
NUM_RINGS = 16        # Number of concentric rings
NUM_SLICES = 32       # Number of angular slices
RADIUS = 2            # Sphere radius
FOV = 180             # Camera FOV in degrees

# -----------------------------
# DELETE EXISTING OBJECTS
# -----------------------------
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# -----------------------------
# CREATE SPHERE
# -----------------------------
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=RADIUS, segments=128, ring_count=128, location=(0,0,0)
)
sphere = bpy.context.active_object
sphere.name = "PolarCheckerSphere"

# Flip normals inward
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.flip_normals()
bpy.ops.object.mode_set(mode='OBJECT')

# -----------------------------
# CREATE MATERIAL
# -----------------------------
mat = bpy.data.materials.new("PolarCheckerMat")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# Clear default nodes
for n in nodes:
    nodes.remove(n)

# Output
output = nodes.new(type='ShaderNodeOutputMaterial')

# Emission shader
emission = nodes.new(type='ShaderNodeEmission')
links.new(emission.outputs['Emission'], output.inputs['Surface'])


# Diffuse
#diffuse = nodes.new(type='ShaderNodeBsdfDiffuse')
#links.new(diffuse.outputs['BSDF'], output.inputs['Surface'])

# Geometry node (get position)
geom = nodes.new(type='ShaderNodeNewGeometry')

# Separate XYZ
separate = nodes.new(type='ShaderNodeSeparateXYZ')
links.new(geom.outputs['Position'], separate.inputs['Vector'])

# Compute r_xy = sqrt(X^2 + Y^2)
combine_xy = nodes.new(type='ShaderNodeCombineXYZ')
links.new(separate.outputs['X'], combine_xy.inputs['X'])
links.new(separate.outputs['Y'], combine_xy.inputs['Y'])
combine_xy.inputs['Z'].default_value = 0.0

r_xy = nodes.new(type='ShaderNodeVectorMath')
r_xy.operation = 'LENGTH'
links.new(combine_xy.outputs['Vector'], r_xy.inputs[0])

# Compute theta = arctan2(r_xy, Z)
theta_node = nodes.new(type='ShaderNodeMath')
theta_node.operation = 'ARCTAN2'
links.new(r_xy.outputs['Value'], theta_node.inputs[0])
links.new(separate.outputs['Z'], theta_node.inputs[1])

# Scale theta to ring index: ring_idx = floor(theta / pi * NUM_RINGS)
theta_scale = nodes.new(type='ShaderNodeMath')
theta_scale.operation = 'MULTIPLY'
theta_scale.inputs[1].default_value = NUM_RINGS / math.pi
links.new(theta_node.outputs['Value'], theta_scale.inputs[0])

theta_floor = nodes.new(type='ShaderNodeMath')
theta_floor.operation = 'FLOOR'
links.new(theta_scale.outputs['Value'], theta_floor.inputs[0])

# Compute phi = atan2(Y,X), map -pi..pi -> 0..2pi
phi_node = nodes.new(type='ShaderNodeMath')
phi_node.operation = 'ARCTAN2'
links.new(separate.outputs['Y'], phi_node.inputs[0])
links.new(separate.outputs['X'], phi_node.inputs[1])

phi_add = nodes.new(type='ShaderNodeMath')
phi_add.operation = 'ADD'
phi_add.inputs[1].default_value = math.pi
links.new(phi_node.outputs['Value'], phi_add.inputs[0])

# Scale phi to slice index: slice_idx = floor(phi / 2pi * NUM_SLICES)
phi_scale = nodes.new(type='ShaderNodeMath')
phi_scale.operation = 'MULTIPLY'
phi_scale.inputs[1].default_value = NUM_SLICES / (2 * math.pi)
links.new(phi_add.outputs['Value'], phi_scale.inputs[0])

phi_floor = nodes.new(type='ShaderNodeMath')
phi_floor.operation = 'FLOOR'
links.new(phi_scale.outputs['Value'], phi_floor.inputs[0])

# Add indices and modulo 2
add_indices = nodes.new(type='ShaderNodeMath')
add_indices.operation = 'ADD'
links.new(theta_floor.outputs['Value'], add_indices.inputs[0])
links.new(phi_floor.outputs['Value'], add_indices.inputs[1])

mod2 = nodes.new(type='ShaderNodeMath')
mod2.operation = 'MODULO'
mod2.inputs[1].default_value = 2
links.new(add_indices.outputs['Value'], mod2.inputs[0])

# Compare > 0.5 to get white/black
greater = nodes.new(type='ShaderNodeMath')
greater.operation = 'GREATER_THAN'
greater.inputs[1].default_value = 0.5
links.new(mod2.outputs['Value'], greater.inputs[0])

# Map 0/1 to colors
color_ramp = nodes.new(type='ShaderNodeValToRGB')
color_ramp.color_ramp.elements[0].color = (0,0,0,1)
color_ramp.color_ramp.elements[1].color = (1,1,1,1)
links.new(greater.outputs['Value'], color_ramp.inputs['Fac'])

# Connect to diffuse
links.new(color_ramp.outputs['Color'], diffuse.inputs['Color'])

sphere.data.materials.append(mat)

# -----------------------------
# CREATE CAMERA
# -----------------------------
bpy.ops.object.camera_add(location=(0,0,0))
cam = bpy.context.active_object
cam.name = "FisheyeCam"
cam.data.type = 'PANO'
cam.data.cycles.panorama_type = 'FISHEYE_EQUISOLID'
cam.data.angle = math.radians(FOV)

bpy.context.scene.camera = cam
bpy.context.scene.render.engine = 'CYCLES'

print("Setup complete: polar checkerboard mapped to sphere, camera at center.")
