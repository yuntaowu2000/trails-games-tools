from Crypto.Cipher import Blowfish
import zstandard as zstd
import sys, os
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

def main(fn):
    '''
        Read and decode (maybe decompress) the file from Kuro no Kiseki.
        Output files will be in the *out* folder under the same directory.
        DDS files will be converted to PNG files.
    '''
    need_decompression = True
    with open(fn, "rb") as f:
        magic = f.read(4)
        if magic == b'C9BA' or magic == b'F9BA':
            data = decrypt(f)
            if data[0:4] == b'D9BA':
                compressed_size = data[4:8]
                compressed_size = int.from_bytes(compressed_size, "little")
                data = data[8:8+compressed_size]
            else:
                decompressed = data
                need_decompression = False
        elif magic == b'D9BA':
            compressed_size = f.read(4)
            compressed_size = int.from_bytes(compressed_size, "little")
            data = f.read(compressed_size)
        else:
            print("unsupported header")
            return
        if need_decompression:
            decompressed = zstd.decompress(data)

    if not os.path.exists("out"):
        os.mkdir("out")

    out_fn = "out\\" + fn.split("\\")[-1]

    with open(out_fn, "wb") as f:
        f.write(decompressed)

    if out_fn.endswith("dds"):
        im = Image.open(out_fn)
        im.save(out_fn[:-3] + "png")

if __name__ == "__main__":
    fn = sys.argv[1]
    main(fn)