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

    curr_rot = [float(r) / math.pi * 180.0 for r in rot[i].split(",")]

    curr_scale = [float(s) for s in scale[i].split(",")]

    bpy.ops.import_scene.gltf(filepath="D:\\kiseki_files\\test\\" + map_asset[i])
    ob = bpy.context.object
    ob.location = (curr_pos[0], -curr_pos[2], curr_pos[1])
    ob.rotation_euler = (-90.0, curr_rot[2], curr_rot[1])
    ob.scale = (curr_scale[0], curr_scale[1], curr_scale[2])

bpy.ops.export_scene.gltf(filepath="D:\\kiseki_files\\test\\test.glb", export_animations=False,export_frame_range=False)