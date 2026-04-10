
# ImportAssets.py

# Imports an object asset by 'linking' from a specified .blend file and duplicates that asset 
# the specified number of instances, updating the 2D (x,y) location, rotation, and scale specified
# in the input list. Asset objects are positioned in the Z-dimension so that their origin is
# located on the terrain mesh (if specified), which may be a 3D ground plane.
#


import bpy
import os


# Generate terrain mask image from b-spline



# Generate list of pseudo-random positions within mask


GroundPlaneMesh = bpy.data.objects['terrain'] 	# 


# Import asset instance
asset_file 		= '/Users/murphyap/Documents/Blender/MF3D/AvatarIdentities_Asset_V1.blend'
asset_object 	= 'Collection'
asset_name 		= 'AvatarBase'

bpy.ops.wm.append(
	filepath=os.path.join(asset_file, asset_object, asset_name),
    directory=os.path.join(asset_file, asset_object),
    filename=asset_name
    )


# Duplicate asset and relocate, rotate and scale




