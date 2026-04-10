import bpy

# --------------------------------------------------
# Clean up the scene
# --------------------------------------------------
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 240

# --------------------------------------------------
# Set gravity
# --------------------------------------------------
scene.gravity = (0, 0, -9.81)

# --------------------------------------------------
# Create ground plane
# --------------------------------------------------
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"

# Add rigid body to ground
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'
ground.rigid_body.restitution = 0.8   # bounciness
ground.rigid_body.friction = 0.8

# --------------------------------------------------
# Create ball
# --------------------------------------------------
radius = 0.5
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=radius,
    location=(0, 0, 5)
)
ball = bpy.context.active_object
ball.name = "Ball"

# Add rigid body to ball
bpy.ops.rigidbody.object_add()
ball.rigid_body.type = 'ACTIVE'
ball.rigid_body.mass = 1.0
ball.rigid_body.restitution = 1.2   # bounciness
ball.rigid_body.friction = 0.4
ball.rigid_body.linear_damping = 0.0
ball.rigid_body.angular_damping = 0.1

# Use sphere collision shape (important!)
ball.rigid_body.collision_shape = 'SPHERE' 

# --------------------------------------------------
# Improve simulation stability
# --------------------------------------------------
scene.rigidbody_world.steps_per_second = 120
scene.rigidbody_world.solver_iterations = 20

print("Rigid-body ball bounce simulation created!")
