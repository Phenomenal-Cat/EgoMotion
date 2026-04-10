import bpy

# ================= SETTINGS =================

MAT_NAME = "Voronoi_Tiles_Cracks"

TILE_SCALE = 10.0       # Number of tiles
JITTER = 0.8            # Voronoi randomness

CRACK_WIDTH = 0.02
EDGE_SOFTNESS = 0.03

TILE_HEIGHT = 0.1

# ===========================================


def create_voronoi_crack_material():
    mat = bpy.data.materials.new(MAT_NAME)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    # Nodes
    output = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")

    texcoord = nodes.new("ShaderNodeTexCoord")
    mapping = nodes.new("ShaderNodeMapping")

    voronoi = nodes.new("ShaderNodeTexVoronoi")
    voronoi.feature = 'DISTANCE_TO_EDGE'
    voronoi.distance = 'EUCLIDEAN'

    maprange = nodes.new("ShaderNodeMapRange")
    maprange.inputs["From Min"].default_value = CRACK_WIDTH
    maprange.inputs["From Max"].default_value = CRACK_WIDTH + EDGE_SOFTNESS
    maprange.inputs["To Min"].default_value = 1.0
    maprange.inputs["To Max"].default_value = 0.0
    maprange.clamp = True

    displacement = nodes.new("ShaderNodeDisplacement")
    displacement.inputs["Scale"].default_value = TILE_HEIGHT

    # Settings
    mapping.inputs["Scale"].default_value = (TILE_SCALE, TILE_SCALE, 1)
    voronoi.inputs["Randomness"].default_value = JITTER

    # Links
    links.new(texcoord.outputs["UV"], mapping.inputs["Vector"])
    links.new(mapping.outputs["Vector"], voronoi.inputs["Vector"])
    links.new(voronoi.outputs["Distance"], maprange.inputs["Value"])
    links.new(maprange.outputs["Result"], displacement.inputs["Height"])

    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    links.new(displacement.outputs["Displacement"], output.inputs["Displacement"])

    # Layout (editor readability only)
    texcoord.location = (-900, 0)
    mapping.location = (-700, 0)
    voronoi.location = (-450, 0)
    maprange.location = (-200, 0)
    displacement.location = (50, -200)
    bsdf.location = (50, 0)
    output.location = (250, 0)

    return mat


mat = create_voronoi_crack_material()
print(f"Material '{mat.name}' created.")
