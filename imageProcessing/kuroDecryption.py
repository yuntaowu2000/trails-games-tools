from Crypto.Cipher import Blowfish
import zstandard as zstd
import sys
from PIL import Image

KEY = b'\x16\x4B\x7D\x0F\x4F\xA7\x4C\xAC\xD3\x7A\x06\xD9\xF8\x6D\x20\x94'
IV = b'\x9D\x8F\x9D\xA1\x49\x60\xCC\x4C'

def decrypt(encrypted_file):
    # Decryption may not work for all scena files
    size = int.from_bytes(encrypted_file.read(4), byteorder='little')
    file = encrypted_file.read(size -  size % Blowfish.block_size)
    cipher = Blowfish.new(KEY, Blowfish.MODE_CTR, initial_value=IV, nonce=b'')
    output = cipher.decrypt(file)
    return output

def decompress(data, compressed_size):
    return zstd.decompress(data)

def main(fn):
    with open(fn, "rb") as f:
        magic = f.read(4)
        if magic == b'C9BA' or magic == b'F9BA':
            data = decrypt(f)
            if data[0:4] == b'D9BA':
                compressed_size = data[4:8]
                compressed_size = int.from_bytes(compressed_size, "little")
                data = data[8:8+compressed_size]
            else:
                print("unsupported")
                return
        else:
            compressed_size = f.read(4)
            compressed_size = int.from_bytes(compressed_size, "little")
            data = f.read(compressed_size)
        decompressed = decompress(data, compressed_size)

    out_fn = "out\\" + fn.split("\\")[-1]

    with open(out_fn, "wb") as f:
        f.write(decompressed)

    if out_fn.endswith("dds"):
        f = out_fn
        im = Image.open(f)
        im = im.transpose(Image.FLIP_TOP_BOTTOM)
        im.save(f[:-3] + "png")

if __name__ == "__main__":
    fn = sys.argv[1]
    # fn = "E:\\SteamLibrary\\steamapps\\common\\THE LEGEND OF HEROES KURO NO KISEKI\\f\\scene\\c0010.json"
    main(fn)