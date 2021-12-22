import json, os, sys, math

# replace with the map name e.g. t0000
map_id = sys.argv[1]
scene_json_name = "D:\\kuro models\\" + map_id +".json"

data_list = []

mdl_to_unpack = set()

with open(scene_json_name, "r") as f:
    val = f.read()

json_obj = json.loads(val)
actors = json_obj["Actor"]
for v in actors:
    if v["type"] != "MapObject": continue

    curr_data = {}
    curr_data["name"] = v["name"]
    curr_data["map_asset"] = v["model_path"] + ".glb"
    if not os.path.exists(v["model_path"] + ".mdl"):
        mdl_to_unpack.add(v["model_path"] + ".mdl")
    
    curr_data["pos"] = str(v["translation"]["x"]) + "," + str(v["translation"]["y"]) + "," + str(v["translation"]["z"])
    
    # to get consistency with sen models
    # easier integration in blender
    curr_data["rot"] = str(v["rotation"]["x"] / 180 * math.pi) + "," + str(v["rotation"]["y"] / 180 * math.pi) + "," + str(v["rotation"]["z"] / 180 * math.pi)

    curr_data["scale"] = str(v["scale"]["x"]) + "," + str(v["scale"]["y"]) + "," + str(v["scale"]["z"])

    data_list.append(curr_data)

data_json = json.dumps(data_list, indent=4)

with open(map_id + ".json", "w") as f:
    f.write(data_json)

