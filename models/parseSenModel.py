from bs4 import BeautifulSoup
from pkgtoglb import standalone_main
import json
# import threading
import os, sys

# replace with path to game files
# ops xml files records all the objects in a scene
map_id = sys.argv[1]
xml_file = "E:\\SteamLibrary\\steamapps\\common\\THE LEGEND OF HEROES HAJIMARI NO KISEKI\\data\\ops\\" + map_id + ".ops"
path = "E:\\SteamLibrary\\steamapps\\common\\THE LEGEND OF HEROES HAJIMARI NO KISEKI\\data\\asset\\D3D11\\"

with open(xml_file, 'r') as f:
    data = f.read()

bs_data = BeautifulSoup(data, "xml")

assets = bs_data.find_all("AssetObject")

pkg_to_unpack = set()
data_list = []

for asset in assets:
    # # currently only house, obj and main map are considered.
    # if asset["asset"][0] == "M" or "HOU" in asset["asset"] or "OBJ" in asset["asset"]:
    curr_data = {}
    curr_data["name"] = asset["asset"]
    curr_data["map_asset"] = asset["asset"][2:].lower() + ".glb"
    if not os.path.exists(asset["asset"] + ".pkg"):
        pkg_to_unpack.add(asset["asset"] + ".pkg")
    curr_data["pos"] = asset["pos"]
    curr_data["rot"] = asset["rot"]
    curr_data["scale"] = asset["scl"]
    data_list.append(curr_data)

data_json = json.dumps(data_list, indent=4)

with open(map_id + ".json", "w") as f:
    f.write(data_json)

if path[-4:] == ".pka":
    from unpackpka import unpack
    unpack(path, pkg_to_unpack)
else:
    import shutil
    for pkg_name in pkg_to_unpack:
        fp = path + pkg_name
        shutil.copy(fp, "./")

failed_pkgs = []
def target_wrapper(pkg):
    try:
        standalone_main(pkg)
    except:
        failed_pkgs.append(pkg)

for pkg in pkg_to_unpack:
    target_wrapper(pkg)

if os.path.isfile("texconv.exe"):
    # change all model dds files to dxt 1 format so that Blender can read them
    os.system("for %f in (*.dds) do texconv.exe -f DXT1 %f -y")

if len(failed_pkgs) > 0:
    # zstd decompression may fail when there are too many threads
    print("failed files: {0}".format(failed_pkgs))
