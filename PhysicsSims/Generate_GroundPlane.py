import bpy
import math
import os

# ================== USER SETTINGS ==================

# Plane
PLANE_NAME  = "Ground_Plane"
WIDTH       = 200.0             # X dimension
DEPTH       = 200.0             # Y dimension
LOCATION    = (0, 0, 0)
ROTATION_DEG = (0, 0, 0)        # Euler rotation in degrees

# Geometry detail
SUBDIV_LEVELS       = 0      # Higher = smoother displacement
DISPLACE_STRENGTH   = 0.5
DISPLACE_MIDLEVEL   = 0.0

# Texture
TEXTURE_PATH    = "ground_diffuse.jpg"
TEXTURE_SCALE   = 5.0   # UV tiling scale

# Material
MATERIAL_NAME   = "Ground_Material"

# ===================================================


def create_ground_plane():
    # Delete existing plane with same name
    if PLANE_NAME in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[PLANE_NAME], do_unlink=True)

    # Create plane
    bpy.ops.mesh.primitive_plane_add(
        size=1,
        location=LOCATION,
        rotation=tuple(math.radians(r) for r in ROTATION_DEG)
    )

    plane = bpy.context.active_object
    plane.name = PLANE_NAME

    # Scale to desired dimensions
    plane.scale.x = WIDTH / 2
    plane.scale.y = DEPTH / 2

    # Apply scale
    bpy.ops.object.transform_apply(scale=True)

    return plane


def add_subdivision(obj):
    subdiv = obj.modifiers.new(name="Subdivision", type='SUBSURF')
    subdiv.levels = SUBDIV_LEVELS
    subdiv.render_levels = SUBDIV_LEVELS


def add_displacement(obj, image_path):
    # Load texture
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Texture not found: {image_path}")

    image = bpy.data.images.load(image_path, check_existing=True)

    tex = bpy.data.textures.new("DisplaceTexture", type='IMAGE')
    tex.image = image

    disp = obj.modifiers.new(name="Displacement", type='DISPLACE')
    disp.texture = tex
    disp.strength = DISPLACE_STRENGTH
    disp.mid_level = DISPLACE_MIDLEVEL
    disp.texture_coords = 'UV'


def create_material(image_path):
    mat = bpy.data.materials.get(MATERIAL_NAME)
    if not mat:
        mat = bpy.data.materials.new(MATERIAL_NAME)

    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    # Nodes
    output = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    tex = nodes.new("ShaderNodeTexImage")
    mapping = nodes.new("ShaderNodeMapping")
    texcoord = nodes.new("ShaderNodeTexCoord")

    # Load image
    tex.image = bpy.data.images.load(image_path, check_existing=True)

    # Layout
    texcoord.location = (-800, 0)
    mapping.location = (-600, 0)
    tex.location = (-400, 0)
    bsdf.location = (-200, 0)
    output.location = (0, 0)

    # UV scaling
    mapping.inputs["Scale"].default_value = (
        TEXTURE_SCALE,
        TEXTURE_SCALE,
        1
    )

    # Links
    links.new(texcoord.outputs["UV"], mapping.inputs["Vector"])
    links.new(mapping.outputs["Vector"], tex.inputs["Vector"])
    links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

    return mat


def assign_material(obj, mat):
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)


# ================== EXECUTION ==================

plane = create_ground_plane()
add_subdivision(plane)
add_displacement(plane, TEXTURE_PATH)

material = create_material(TEXTURE_PATH)
assign_material(plane, material)

print("Ground plane created successfully.")
