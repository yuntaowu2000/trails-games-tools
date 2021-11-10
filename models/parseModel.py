from bs4 import BeautifulSoup
from pkgtoglb import standalone_main
import json
import threading
import os

# replace with path to game files
# ops xml files records all the objects in a scene
xml_file = "E:\\SteamLibrary\\steamapps\\common\\THE LEGEND OF HEROES HAJIMARI NO KISEKI\\data\\ops\\c1400.ops"
path = "E:\\SteamLibrary\\steamapps\\common\\THE LEGEND OF HEROES HAJIMARI NO KISEKI\\data\\asset\\D3D11\\"

with open(xml_file, 'r') as f:
    data = f.read()

bs_data = BeautifulSoup(data, "xml")

assets = bs_data.find_all("AssetObject")

map_asset = []
pkg_to_unpack = set()
pos = []
rot = []
scale = []
threads = set()

for asset in assets:
    # currently only house, obj and main map are considered.
    if asset["asset"][0] == "M" or "HOU" in asset["asset"] or "OBJ" in asset["asset"]:
        map_asset.append(asset["asset"][2:].lower() + ".glb")
        pkg_to_unpack.add(asset["asset"] + ".pkg")
        pos.append(asset["pos"])
        rot.append(asset["rot"])
        scale.append(asset["scl"])

data_dict = {
    "map_asset": map_asset,
    "pos" : pos,
    "rot" : rot,
    "scale" : scale
}

data_json = json.dumps(data_dict, indent=4)

with open("data.json", "w") as f:
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
    t = threading.Thread(target=lambda:target_wrapper(pkg))
    threads.add(t)
    t.start()

for t in threads:
    t.join()

if os.path.isfile("texconv.exe"):
    # change all model dds files to dxt 1 format so that Blender can read them
    os.system("for %f in (*.dds) do texconv.exe -f DXT1 %f -y")

if len(failed_pkgs) > 0:
    # zstd decompression may fail when there are too many threads
    print("failed files: {0}".format(failed_pkgs))
