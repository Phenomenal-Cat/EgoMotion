

import bpy
import bmesh
import math
import random
import numpy as np
from mathutils import Vector


# Clear scene
#bpy.ops.object.select_all(action='SELECT')
#bpy.ops.object.delete(use_global=False)


# Camera setup


# Ball Distribution within specified radii
BallDiameter    = 0.3
HeightRange 	= [1, 10]
DistanceRange 	= [5, 20]
Density 		= 0.3															 # Density of balls in number of balls per meter squared
Area 			= ((np.pi*DistanceRange[1]**2)-(np.pi*DistanceRange[0]**2))/2 	 # Floor area for balls in meters squared
TotalBalls 		= int(np.round(Area/BallDiameter*Density))									 # Calculate total number of balls in scene

Balls_Heights 	= np.random.uniform(HeightRange[0],HeightRange[1],TotalBalls) 		     # Generate random starting height per ball
Balls_Theta  	= np.random.uniform(np.deg2rad(-180), np.deg2rad(180), TotalBalls) 	      # Generate random azimuth angles per ball
Balls_Radius  	= np.random.uniform(DistanceRange[0], DistanceRange[1], TotalBalls) 	   # Generate random starting distances per ball

x_coords = [r * math.cos(t) for t, r in zip(Balls_Theta, Balls_Radius)]
y_coords = [r * math.sin(t) for t, r in zip(Balls_Theta, Balls_Radius)]
abs_y_coords = [abs(y) for y in y_coords]


# Ball Properties
Ball_ScaleRange 		= [0.5, 2]
Ball_BouncinessRage 	= [0.5, 1.5]
Ball_WeightRange 		= []
Ball_Newtonian 			= False


Balls_Scales = np.random.uniform(Ball_ScaleRange[0], Ball_ScaleRange[1], TotalBalls)


# Gravitational forces
Gravity_Earth			= Vector((0.0, 0.0, -9.81))
Gravity_Moon 			= Vector((0.0, 0.0, -1.62))
Gravity_Jupiter 		= Vector((0.0, 0.0, -24.8))


#===== Generate initial ball mesh
mesh    = bpy.data.meshes.new("Ball_mesh")
bm      = bmesh.new()
bmesh.ops.create_uvsphere(
    bm,
    u_segments  =16,   # lower = faster
    v_segments  =8,
    radius      =(BallDiameter/2)
)
bm.to_mesh(mesh)
bm.free()

#===== Create linked object per ball
collection = bpy.context.collection
for i in range(TotalBalls):
    obj = bpy.data.objects.new(f"Ball_{i:03d}", mesh)
    collection.objects.link(obj)
    obj.location = (x_coords[i], abs_y_coords[i], Balls_Heights[i])
    obj.scale = (Balls_Scales[i], Balls_Scales[i],Balls_Scales[i])
    
    # Apply scale
    bpy.context.view_layer.objects.active = obj     
    bpy.ops.object.shade_smooth()                   # Smooth shading
    bpy.ops.object.transform_apply(
        location=False,
        rotation=False,
        scale=True
    )
    
    if not obj:
        printf('Object is NoneType')
    else:
        if obj.name in bpy.data.objects:
            if obj.rigid_body is not None:
                obj.rigid_body.collision_shape = 'SPHERE'
    


    

#====== Generate sphere objects
#for ball in range(0, TotalBalls):
#    obj_name    = f"Ball_{ball:03d}"
#    mesh_name   = f"{obj_name}_Mesh"
#    mesh        = bpy.data.meshes.new(mesh_name)
#    obj         = bpy.data.objects.new(obj_name, mesh)
#    bpy.context.collection.objects.link(obj)
#    obj.location    = (x_coords[ball], abs_y_coords[ball], Balls_Heights[ball])
#    bm = bmesh.new()
#    bmesh.ops.create_uvsphere(
#        bm,
#        u_segments  =32,
#        v_segments  =16,
#        radius      =(BallDiameter/2)*Balls_Scales[ball]
#    )
#    bm.to_mesh(mesh)
#    bm.free()
    

#====== Apply standard gravity to each ball
bpy.context.scene.use_gravity = True
bpy.context.scene.gravity = (0, 0, -9.81)

for ball in bpy.data.objects:
    if ball.name.startswith("Ball_"):
        bpy.context.view_layer.objects.active = ball

        bpy.ops.rigidbody.object_add()
        ball.rigid_body.type = 'ACTIVE'
        ball.rigid_body.mass = 1.0
        ball.rigid_body.friction = 0.5
        ball.rigid_body.restitution = 0.2  # bounce
        ball.rigid_body.collision_shape = 'SPHERE'


# Ground plane
ground = bpy.data.objects['Ground_Plane']
bpy.context.view_layer.objects.active = ground
bpy.ops.rigidbody.object_add()

ground.rigid_body.type = 'PASSIVE'
ground.rigid_body.friction = 0.8
ground.rigid_body.restitution = 0.0
ground.rigid_body.collision_shape = 'BOX'

# Ensure rigid body world exists
scene = bpy.context.scene
if not scene.rigidbody_world:
    bpy.ops.rigidbody.world_add()

rbw = scene.rigidbody_world
rbw.steps_per_second = 120      # stable, not too slow
rbw.solver_iterations = 10      # lower for many bodies


# Bake simulation
bpy.ops.ptcache.free_bake_all()
bpy.ops.ptcache.bake_all()



"""

# Per-object gravity vectors (m/s^2)
# Object names must match exactly
CUSTOM_GRAVITY = {
    "Ball_A": Vector((0.0, 0.0, -9.81)),     # Earth gravity
    "Ball_B": Vector((5.0, 0.0, -15.0)),     # Strong diagonal gravity
    "Ball_C": Vector((0.0, 0.0, 9.81)),      # Anti-gravity
}

# --------------------------------------------------
# SETUP: disable gravity for these objects
# --------------------------------------------------

for obj_name in CUSTOM_GRAVITY:
    obj = bpy.data.objects.get(obj_name)
    if obj is None:
        print(f"Object '{obj_name}' not found")
        continue

    if obj.rigid_body is None:
        print(f"Object '{obj_name}' has no rigid body")
        continue

    obj.rigid_body.use_gravity = False


# --------------------------------------------------
# FRAME HANDLER: apply custom gravity every frame
# --------------------------------------------------

def apply_custom_gravity(scene):
    for obj_name, g_vec in CUSTOM_GRAVITY.items():
        obj = bpy.data.objects.get(obj_name)
        if obj is None or obj.rigid_body is None:
            continue

        mass = obj.rigid_body.mass
        force = mass * g_vec

        # Apply force at center of mass
        obj.rigid_body.apply_force(force, location=False)


# --------------------------------------------------
# REGISTER HANDLER (avoid duplicates)
# --------------------------------------------------

handlers = bpy.app.handlers.frame_change_pre
if apply_custom_gravity not in handlers:
    handlers.append(apply_custom_gravity)

print("Custom per-object gravity enabled.")

"""