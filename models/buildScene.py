# this code can only be run in blender
import math
import bpy
import json
import os

# replace with path to the json output from parseModel.py
folder_path = "D:\\test\\"
json_name = "c0000.json"
with open(folder_path + json_name, "r") as f:
   data = json.loads(f.read())

for i in range(len(data)):
   fp = folder_path + data[i]["map_asset"]
   if not os.path.exists(fp): continue
   curr_pos = [float(p) for p in data[i]["pos"].split(",")]

   curr_rot = [float(r) for r in data[i]["rot"].split(",")]

   curr_scale = [float(s) for s in data[i]["scale"].split(",")]

   # replace with path to the path with all related glb files
   bpy.ops.import_scene.gltf(filepath=fp)
   ob = bpy.context.object
   ob.location = (curr_pos[0], -curr_pos[2], curr_pos[1])

   ob.rotation_mode = 'XYZ'
   # for blender version 2.93, 
   # blender changes the behavior of XYZ rotation (from radian to degree) in some update
   ob.rotation_euler = (curr_rot[0], curr_rot[2], curr_rot[1])
   
   # for blender version 2.82, can use the following
   # ob.rotation_euler = (math.pi / 2, curr_rot[2], curr_rot[1])
   ob.scale = (curr_scale[0], curr_scale[1], curr_scale[2])
   ob.name = data[i]["name"]

shapes_to_exclude = ["CA", "CK", "CO", "CS", "CP"]

for obj in bpy.context.scene.objects: 
   if obj.name[0:2] in shapes_to_exclude or "shadow" in obj.name or "light_locator" in obj.name or "light_all" in obj.name:
      # collider, shadow, lights
      obj.select_set(state=True)
   if "directionalLight" in obj.name or "bill" in obj.name or "box_" in obj.name or "half_sphere" in obj.name or:
      # light effects, skybox
      obj.select_set(state=True)
   if "_etc" in obj.name or "window_dawn" in obj.name or "window_evening" in obj.name or "window_morning" in obj.name or "window_night" in obj.name:
      # windows
      obj.select_set(state=True)
bpy.ops.object.delete()

#import bpy
#import os

#folder_path = "D:\\crossbell\\processed\\"

#for root, dirs, files in os.walk(folder_path):
#    for file in files:
#        if file.endswith(".gltf"):
#            fp = os.path.join(root,file)
#            out = os.path.join(root, file[:-5] + ".obj")
#            bpy.ops.import_scene.gltf(filepath=fp)
#            bpy.ops.export_scene.obj(filepath=out)
#            for obj in bpy.context.scene.objects: 
#                obj.select_set(state=True)
#            bpy.ops.object.delete()
