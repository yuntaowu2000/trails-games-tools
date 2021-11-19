# this code can only be run in blender
import math
import bpy
import json
import os

# replace with path to the data.json output from parseModel.py
folder_path = "D:\\test\\"
with open(folder_path + "data.json", "r") as f:
   data = json.loads(f.read())
   map_asset = data["map_asset"]
   pos = data["pos"]
   rot = data["rot"]
   scale = data["scale"]

for i in range(len(map_asset)):
   fp = folder_path + map_asset[i]
   if not os.path.exists(fp): continue
   curr_pos = [float(p) for p in pos[i].split(",")]

   # remove any outliers (they are mostly background objects that are not really related to the map)
   if abs(curr_pos[0]) > 200 or abs(curr_pos[1]) > 200 or abs(curr_pos[2]) > 200: continue

   curr_rot = [float(r) for r in rot[i].split(",")]

   curr_scale = [float(s) for s in scale[i].split(",")]

   # replace with path to the path with all related glb files
   bpy.ops.import_scene.gltf(filepath=fp)
   ob = bpy.context.object
   ob.location = (curr_pos[0], -curr_pos[2], curr_pos[1])
   # for blender version 2.93, 
   # blender changes the behavior of XYZ rotation (from radian to degree) in some update
   ob.rotation_quaternion = (1.0, curr_rot[0], -curr_rot[2], curr_rot[1])
   # for blender version 2.82, can use the following
   # ob.rotation_mode = 'XYZ'
   # ob.rotation_euler = (math.pi / 2, curr_rot[2], curr_rot[1])
   ob.scale = (curr_scale[0], curr_scale[1], curr_scale[2])

shapes_to_exclude = ["CA", "CK", "CO", "CS", "CP"]

for obj in bpy.context.scene.objects: 
   if obj.name[0:2] in shapes_to_exclude or "shadow" in obj.name or "light_locator" in obj.name or "light_all" in obj.name or "window_dawn" in obj.name or "window_evening" in obj.name or "window_morning" in obj.name or "window_night" in obj.name:
      obj.select_set(state=True)
   if "directionalLight" in obj.name:
      obj.select_set(state=True)
bpy.ops.object.delete()