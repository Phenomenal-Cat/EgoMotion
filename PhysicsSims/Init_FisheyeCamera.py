
# InitFisheyeScene

import math
import mathutils as mu
import bpy


Resolution         	= [1080, 1080] 
StereoFormat 		= 0
ViewingDistance     = 0.2


#============ Set scene settings
Scene                                       = bpy.data.scenes[0]
Scene.unit_settings.system                  = 'METRIC'
Scene.render.engine                         = 'CYCLES'
Scene.render.resolution_x                   = Resolution[0]
Scene.render.resolution_y                   = Resolution[1]
Scene.render.resolution_percentage          = 100
Scene.render.use_stamp                      = False							# Turn render stamps off
#Scene.render.display_mode                   = 'SCREEN'
Scene.render.image_settings.color_depth     = '8'                           # Set color bit-depth (8 or 16 for PNG)
Scene.render.use_placeholder                = True                          
Scene.cycles.film_transparent               = True


#============ Set stereoscopic 3D settings
StereoSet                                           = bpy.context.scene.render.image_settings
if StereoFormat == 0:                                                   #=========== 2D rendering
    Scene.render.use_multiview                      = False
    #Scene.render.views_format                       = 'INDIVIDUAL'
    #StereoSet.views_format                          = 'INDIVIDUAL' 
elif StereoFormat == 1:                                                 #=========== Side-by-side stereo rendering
    Scene.render.use_multiview                      = True
    Scene.render.views_format                       = 'STEREO_3D'
    StereoSet.views_format                          = 'STEREO_3D'   
    StereoSet.stereo_3d_format.display_mode         = 'SIDEBYSIDE'
    StereoSet.stereo_3d_format.use_sidebyside_crosseyed = False                     # Do not switch eyes
    StereoSet.stereo_3d_format.use_squeezed_frame       = True                  	# Use squeezed frame format
        
elif StereoFormat == 2:                                                 #=========== Anaglyph rendering
    StereoSet.stereo_3d_format.display_mode         = 'ANAGLYPH'
    StereoSet.stereo_3d_format.anaglyph_type        = 'RED_CYAN' 


camera_exists = any(obj.type == 'CAMERA' for obj in bpy.data.objects)
if not(camera_exists):
    bpy.ops.object.camera_add()
    Scene.camera = bpy.context.active_object
    
Cam2                                                = bpy.data.cameras["Camera"]
Cam2.stereo.interocular_distance                    = 0.035                         # Set for average Rhesus macaque IPD (meters)
Cam2.stereo.convergence_distance                    = ViewingDistance/100           # Cameras converge at screen distance from viewer
Cam2.stereo.convergence_mode                        = 'OFFAXIS'                     # Off-axis frusta are required for physically correct renders

    
#============ Set camera settings
Cam                                                 = bpy.data.objects["Camera"]
Cam.location                                        = mu.Vector((0, 0,0))
Cam.rotation_euler 									= mu.Vector((math.radians(90), 0, 0))
Scene.camera.data.type                          	= 'PANO'
Scene.camera.data.cycles.panorama_type          	= 'FISHEYE_EQUIDISTANT'  
Scene.render.resolution_x                       	= Resolution[1]
Scene.render.resolution_y                       	= Resolution[1]


