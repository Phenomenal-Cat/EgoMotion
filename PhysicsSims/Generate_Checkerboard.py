import bpy

# -----------------------------
# SCENE SETUP
# -----------------------------
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.feature_set = 'EXPERIMENTAL'
bpy.context.scene.cycles.device = 'GPU'
bpy.context.scene.unit_settings.system = 'METRIC'
bpy.context.scene.unit_settings.scale_length = 1.0

# -----------------------------
# DELETE DEFAULT OBJECTS
# -----------------------------
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# -----------------------------
# CREATE GROUND PLANE
# -----------------------------
bpy.ops.mesh.primitive_plane_add(size=1000, location=(0, 0, 0))
ground = bpy.context.object
ground.name = "Ground_1000m"

# Apply scale
bpy.ops.object.transform_apply(scale=True)

# -----------------------------
# ADD SUBSURFACE MODIFIER
# -----------------------------
subsurf = ground.modifiers.new(name="Subdivision", type='SUBSURF')
subsurf.subdivision_type = 'SIMPLE'
subsurf.levels = 0
subsurf.render_levels = 0

# Enable adaptive subdivision
ground.cycles.use_adaptive_subdivision = True

# -----------------------------
# CREATE MATERIAL
# -----------------------------
mat = bpy.data.materials.new(name="Checker_Tiles")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links
nodes.clear()

# Output
output = nodes.new(type='ShaderNodeOutputMaterial')

# Principled BSDF
bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
bsdf.inputs["Roughness"].default_value = 0.8

# Texture Coordinate
texcoord = nodes.new(type='ShaderNodeTexCoord')

# Mapping
mapping = nodes.new(type='ShaderNodeMapping')
mapping.inputs["Scale"].default_value = (1, 1, 1)

# Checker Texture (color)
checker = nodes.new(type='ShaderNodeTexChecker')
checker.inputs["Scale"].default_value = 1.0
checker.inputs["Color1"].default_value = (0, 0, 0, 1)
checker.inputs["Color2"].default_value = (1, 1, 1, 1)

# Brick Texture (height / cracks)
brick = nodes.new(type='ShaderNodeTexBrick')
brick.inputs["Scale"].default_value = 1.0
brick.inputs["Mortar Size"].default_value = 0.05
brick.inputs["Bias"].default_value = 0.0

# Displacement
displacement = nodes.new(type='ShaderNodeDisplacement')
displacement.inputs["Scale"].default_value = 0.05
displacement.inputs["Midlevel"].default_value = 0.5

# -----------------------------
# CONNECT NODES
# -----------------------------
links.new(texcoord.outputs["UV"], mapping.inputs["Vector"])

links.new(mapping.outputs["Vector"], checker.inputs["Vector"])
links.new(mapping.outputs["Vector"], brick.inputs["Vector"])

links.new(checker.outputs["Color"], bsdf.inputs["Base Color"])
links.new(brick.outputs["Fac"], displacement.inputs["Height"])

links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
links.new(displacement.outputs["Displacement"], output.inputs["Displacement"])

# -----------------------------
# MATERIAL SETTINGS
# -----------------------------
mat.cycles.displacement_method = 'DISPLACEMENT'

ground.data.materials.append(mat)

# -----------------------------
# CAMERA (OPTIONAL)
# -----------------------------
bpy.ops.object.camera_add(location=(0, -1200, 800), rotation=(1.1, 0, 0))
bpy.context.scene.camera = bpy.context.object

# -----------------------------
# LIGHT (OPTIONAL)
# -----------------------------
bpy.ops.object.light_add(type='SUN', location=(0, 0, 500))
bpy.context.object.data.energy = 5

print("✔ Ground plane with 1m checker tiles and displacement created.")
