import bpy
import math

# --------------------------------------------------
# Clean up the scene
# --------------------------------------------------
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 300
scene.gravity = (0, 0, -9.81)

# --------------------------------------------------
# Create uneven ground
# --------------------------------------------------
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Uneven_Ground"

# Rotate to make it sloped
ground.rotation_euler[1] = math.radians(10)  # slope angle

# Subdivision for smooth deformation
subsurf = ground.modifiers.new(name="Subsurf", type='SUBSURF')
subsurf.levels = 3

# Displace modifier for uneven surface
disp = ground.modifiers.new(name="Displace", type='DISPLACE')
disp.strength = 0.5

# Create noise texture for displacement
tex = bpy.data.textures.new("GroundNoise", type='CLOUDS')
tex.noise_scale = 2.0
disp.texture = tex

# Apply modifiers (important for rigid body accuracy)
bpy.ops.object.modifier_apply(modifier=subsurf.name)
bpy.ops.object.modifier_apply(modifier=disp.name)

# Add rigid body to ground
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'
ground.rigid_body.friction = 0.9
ground.rigid_body.restitution = 0.5
ground.rigid_body.collision_shape = 'MESH'

# --------------------------------------------------
# Create ball
# --------------------------------------------------
radius = 0.5
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=radius,
    location=(0, 0, 6)
)
ball = bpy.context.active_object
ball.name = "Ball"

# Add rigid body to ball
bpy.ops.rigidbody.object_add()
ball.rigid_body.type = 'ACTIVE'
ball.rigid_body.mass = 1.0
ball.rigid_body.restitution = 0.6
ball.rigid_body.friction = 0.4
ball.rigid_body.linear_damping = 0.05
ball.rigid_body.angular_damping = 0.05
ball.rigid_body.collision_shape = 'SPHERE'

# --------------------------------------------------
# Improve simulation quality
# --------------------------------------------------
scene.rigidbody_world.steps_per_second = 120
scene.rigidbody_world.solver_iterations = 20

print("Sloped and uneven rigid-body ground created!")
