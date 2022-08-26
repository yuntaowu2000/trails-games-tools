from Crypto.Cipher import Blowfish
import zstandard as zstd
import json, os, sys, math, shutil, io
from mdlToGlb import read_mdl_to_gltf
from PIL import Image

# key and IV from https://github.com/nnguyen259/KuroTools
KEY = b'\x16\x4B\x7D\x0F\x4F\xA7\x4C\xAC\xD3\x7A\x06\xD9\xF8\x6D\x20\x94'
IV = b'\x9D\x8F\x9D\xA1\x49\x60\xCC\x4C'
def decrypt(encrypted_file):
    sz = encrypted_file.read(4)
    file = encrypted_file.read()
    cipher = Blowfish.new(KEY, Blowfish.MODE_CTR, initial_value=IV, nonce=b'')
    output = cipher.decrypt(file)
    return output

def decrpyt_and_decompress(f):
    need_decompression = True
    magic = f.read(4)
    if magic == b'C9BA' or magic == b'F9BA':
        data = decrypt(f)
        if data[0:4] == b'D9BA':
            compressed_size = data[4:8]
            compressed_size = int.from_bytes(compressed_size, "little")
            data = data[8:8+compressed_size]
        elif data[0:4] == b'\x89PNG':
            decompressed = data
            need_decompression = False
        else:
            print("unknown header")
            return
    elif magic == b'D9BA':
        compressed_size = f.read(4)
        compressed_size = int.from_bytes(compressed_size, "little")
        data = f.read(compressed_size)
    else:
        print("unsupported header")
        return
    if need_decompression:
        decompressed = zstd.decompress(data)
    
    return decompressed

# replace with the map name e.g. t0000 and your own path
map_id = sys.argv[1]
GAME_ROOT = "E:\\SteamLibrary\\steamapps\\common\\THE LEGEND OF HEROES KURO NO KISEKI\\"
BASE_MDL_PATH = GAME_ROOT + "c\\asset\\common\\model\\"
BASE_SCENE_PATH = GAME_ROOT + "f\\scene\\"
BASE_IM_PATH1 = GAME_ROOT + "c\\asset\\dx11\\image\\"
BASE_IM_PATH2 = GAME_ROOT + "tc\\c\\asset\\dx11\\image\\"
scene_json_name = BASE_SCENE_PATH + map_id + ".json"

data_list = []
mdl_to_unpack = set()

print("reading and writing scene data")
try:
    with open(scene_json_name, "r") as f:
        val = f.read()
except:
    # PC encoded/compressed ver
    with open(scene_json_name, "rb") as f:
        val = decrpyt_and_decompress(f)

# write out the parsed json for composing all the components of the map
json_obj = json.loads(val)
actors = json_obj["Actor"]
for v in actors:
    if v["type"] != "MapObject" and v["type"] != "FieldTerrain": continue

    curr_data = {}
    curr_data["name"] = v["name"]
    # curr_data["map_asset"] = v["model_path"] + ".glb"
    curr_data["map_asset"] = v["model_path"] + ".gltf"
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

# decompress or copy the file to current dir
print("decompressing and copying mdl files")
for mdl in mdl_to_unpack:
    original_mdl = BASE_MDL_PATH + mdl
    with open(original_mdl, "rb") as f:
        magic = f.read(4)
        if magic == b"MDL ":
            # no need to decompress
            shutil.copy(original_mdl, "./")
        elif magic in [b'C9BA', b'D9BA', b'F9BA']:
            f.seek(0)
            decompressed = decrpyt_and_decompress(f)
            with open(mdl, "wb") as f1:
                f1.write(decompressed)

# write mdl to gltf
all_images = set()
for mdl in mdl_to_unpack:
    print("decoding ", mdl)
    read_mdl_to_gltf(mdl)
    if os.path.exists(mdl[:-4] + "_images.txt"):
        with open(mdl[:-4] + "_images.txt", "r") as f:
            ims = json.loads(f.read())
            for im in ims:
                all_images.add(im + ".dds")

print("decoding images")
for im in all_images:
    if os.path.exists(BASE_IM_PATH1 + im):
        with open(BASE_IM_PATH1 + im, "rb") as f:
            decompressed = decrpyt_and_decompress(f)
    elif os.path.exists(BASE_IM_PATH2 + im):
        with open(BASE_IM_PATH2 + im, "rb") as f:
            decompressed = decrpyt_and_decompress(f)
    img = Image.open(io.BytesIO(decompressed))
    img.save(im[:-3] + "png")