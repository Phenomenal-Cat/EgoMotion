import math
import numpy as np
import bpy


#======== Set parameters for motpion parallax lateral oscillations
panning_angle       = 20        # Total amplitude of camera rotation (°) during panning
parallax_disp       = 0.1       # Total amplitude of camera lateral displacement (m) during parallax oscillations
seconds_per_cycle   = 4
frames_per_second   = 30
frames_per_cycle    = seconds_per_cycle*frames_per_second

timepoints  = np.linspace(0, 2*math.pi, frames_per_cycle)
magnitudes  = np.sin(timepoints)*parallax_disp
rotations   = np.radians(np.sin(timepoints)*panning_angle)

Cam         = bpy.data.objects["Camera"]
CamStartLoc = Cam.location
CamStartRot = Cam.rotation_euler
Scene       = bpy.data.scenes["Scene"]
Scene.render.fps = frames_per_second

#========= Iterate through frames and insert keyframes
bpy.context.scene.frame_current = 1

for f in range(1, len(magnitudes)+1):
    
    if DoParallax == 1:
        Cam.location        = ((magnitudes[f], CamStartLoc[1], CamStartLoc[2]))
        Cam.keyframe_insert(data_path="location", frame=f)
    else:
        Cam.rotation_euler  = ((CamStartRot[0], CamStartRot[1], rotations[f]))
        Cam.keyframe_insert(data_path="rotation_euler", frame=f) 
        
Scene_frame_start   = 1    
Scene.frame_end     = frames_per_cycle