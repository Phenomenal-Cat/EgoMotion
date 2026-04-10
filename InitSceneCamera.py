
# InitSceneCamera.py

# Opens the specified .blend file scene, creates a new camera object and sets its parameters
# appopriate for rendering fisheye animations for presentation in the NIF dome rig.

import os
import math
import mathutils
import bpy

#======== Find camera by name
def findCamByName(CamName):
    cam_data    = []
    cam_obj     = []
    for c in bpy.data.objects:
        if c.name == CamName:
            cam_obj = c
            print('A camera object named %s already exists in the scene' % (CamName))
    if not cam_obj:
        print('No camera object named %s exists in the scene' % (CamName))
    for c in bpy.data.cameras:
        if c.name == CamName:
            cam_data = bpy.data.cameras[c.name]
            print('Camera data named %s already exists in the scene' % (CamName))
    if not cam_data:
        print('No camera data named %s exists in the scene' % (CamName))
    return cam_data, cam_obj


#======== Create a fisheye camera
def createFisheyeCam(CamName):
    
    # Set render output parameters
    scn.render.resolution_x             = 2160          # Render 1:1 aspect fisheye at 4K res
    scn.render.resolution_y             = 2160          
    scn.render.resolution_percentage    = 100           # Reduce resolution for faster render preview

    [cam, cam_obj]     = findCamByName(CamName)         # Check whether a camera by this name already exists
    
    if not cam:                                         # If not, then...
        cam            = bpy.data.cameras.new(CamName)  # Create a new camera
    if not cam_obj:
        cam_obj        = bpy.data.objects.new(CamName, cam)
        scn.collection.objects.link(cam_obj)
    cam.type           = 'PANO'                         # Set camera type to panoramic
    cam.panorama_type  = 'FISHEYE_EQUIDISTANT'          # Set panorama type to equidistant
    #cam.fisheye_lens   = 10.5                           # Set camera focal length (mm) (type='Equisolid' only)
    cam.fisheye_fov    = math.radians(180)              # Set camera field-of-view in degrees
    cam.clip_start     = 0.001                          # Set start of render clipping distance (m)
    cam.clip_end       = 100                            # Set end of render clipping distance (m)
    return cam_obj, cam

#======== Set camera position
def setCamPos(camObj, Pos_xyz, Rot_xyz):
    camObj.location       = mathutils.Vector(Pos_xyz)
    camObj.rotation_euler = (math.radians(Rot_xyz[0]), math.radians(Rot_xyz[1]), math.radians(Rot_xyz[2]))

#======== Stereoscopic 3D render settings
def setStereoMode(StereoMode, cam):
    if StereoMode == True:
        scn.render.use_multiview                                = True
        scn.render.views_format                                 = 'STEREO_3D'
        scn.render.image_settings.views_format                  = 'STEREO_3D'
        scn.render.image_settings.stereo_3d_format.display_mode = 'SIDEBYSIDE'
        scn.render.image_settings.stereo_3d_format.use_squeezed_frame = True

        cam.stereo.convergence_mode        = 'OFFAXIS'
        cam.stereo.convergence_distance    = 0.3
        cam.stereo.interocular_distance    = 0.035
        cam.stereo.pivot                   = 'CENTER'
        
    elif StereoMode == False:
         scn.render.use_multiview                                = False
    

#======== 
Render_Stereo = False                               # Apply stereoscopic 3D render settings?
scn = bpy.context.scene                             # Get Blender scene handle
scn.unit_settings.scale_length  = 1
scn.unit_settings.length_unit   = 'METERS' 

[CamData, CamObj] = createFisheyeCam("Camera_FishEyeTest")
setCamPos(CamData, [0,0,1], [90,0,45])
setStereoMode(True, CamObj)