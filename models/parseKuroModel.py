import json

scene_json_name = "D:\\Downloads\\CUSA27774-app_psarc\\scene_files\\t0000.json"

name = []
map_asset = []
pos = []
rot = []
scale = []

mdl_to_unpack = set()

with open(scene_json_name, "r") as f:
    val = f.read()
    json_obj = json.loads(val)
    actors = json_obj["Actor"]
    for v in actors:
        if v["type"] == "MapObject":
            name.append(v["name"])
            map_asset.append(v["model_path"] + ".glb")
            mdl_to_unpack.add(v["model_path"] + ".mdl")
            
            pos_str = str(v["translation"]["x"]) + "," + str(v["translation"]["y"]) + "," + str(v["translation"]["z"])
            pos.append(pos_str)

            rot_str = str(v["rotation"]["x"]) + "," + str(v["rotation"]["y"]) + "," + str(v["rotation"]["z"])
            rot.append(rot_str)

            scl_str = str(v["scale"]["x"]) + "," + str(v["scale"]["y"]) + "," + str(v["scale"]["z"])
            scale.append(scl_str)

data_dict = {
    "name": name,
    "map_asset": map_asset,
    "pos" : pos,
    "rot" : rot,
    "scale" : scale
}

data_json = json.dumps(data_dict, indent=4)

with open("data.json", "w") as f:
    f.write(data_json)

