# this code can only be run in blender
import math
import bpy
import json

# replace with path to the data.json output from parseModel.py
with open("D:\\kiseki_files\\test\\data.json", "r") as f:
   data = json.loads(f.read())
   map_asset = data["map_asset"]
   pos = data["pos"]
   rot = data["rot"]
   scale = data["scale"]

for i in range(len(map_asset)):
   curr_pos = [float(p) for p in pos[i].split(",")]

   curr_rot = [float(r) for r in rot[i].split(",")]

   curr_scale = [float(s) for s in scale[i].split(",")]

   # replace with path to the path with all related glb files
   bpy.ops.import_scene.gltf(filepath="D:\\kiseki_files\\test\\" + map_asset[i])
   ob = bpy.context.object
   ob.location = (curr_pos[0], -curr_pos[2], curr_pos[1])
   ob.rotation_mode = 'XYZ'
   ob.rotation_euler = (math.pi / 2, curr_rot[2], curr_rot[1])
   ob.scale = (curr_scale[0], curr_scale[1], curr_scale[2])

shapes_to_exclude = ["CA", "CK", "CO", "CS"]

for obj in bpy.context.scene.objects: 
   if obj.name[0:2] in shapes_to_exclude or obj.name[0:7] == "Yup2Zup" or "light_locator" in obj.name or "light_all" in obj.name or "window_dawn" in obj.name or "window_evening" in obj.name or "window_morning" in obj.name or "window_night" in obj.name:
      obj.select_set(state=True)
        
bpy.ops.object.delete()