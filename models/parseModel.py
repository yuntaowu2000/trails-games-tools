from bs4 import BeautifulSoup
from unpackpka import unpack
from pkgtoglb import standalone_main
import json
import threading

# replace with path to game files
# ops xml files records all the objects in a scene
xml_file = "E:\\games\\The Legend of Heroes Trails of Cold Steel IV\\data\\ops\\c1200.ops"
path4 = "E:\\games\\The Legend of Heroes Trails of Cold Steel IV\\data\\asset\\D3D11\\assets.pka"

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
    # currently only house and main map are considered.
    # can add obj files 
    if asset["asset"][0] == "M" or "HOU" in asset["asset"]:
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

unpack(path4, pkg_to_unpack)

for pkg in pkg_to_unpack:
    t = threading.Thread(target=lambda:standalone_main(pkg))
    threads.add(t)
    t.start()

for t in threads:
    t.join()
