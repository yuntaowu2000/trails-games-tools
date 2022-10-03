# for zero/ao kai itp files
# requires numpy
# code adopted from https://github.com/Coxxs/itpcnv-dana
import struct, sys
from PIL import Image

def get_dds_header(height: int, width: int):
    header = bytearray(
        [
        0x44, 0x44, 0x53, 0x20, # magic: DDS 
        0x7C, 0x00, 0x00, 0x00, # head size
        0x06, 0x00, 0x00, 0x00, # flags: DDSD_HEIGHT | DDSD_WIDTH
        0x00, 0x00, 0x00, 0x00, # height
        0x00, 0x00, 0x00, 0x00, # width
        0x00, 0x00, 0x00, 0x00, # pitchOrLinearSize
        0x00, 0x00, 0x00, 0x00, # depth
        0x01, 0x00, 0x00, 0x00, # mipMapCount: 1
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x20, 0x00, 0x00, 0x00,
        0x04, 0x00, 0x00, 0x00, 0x44, 0x58, 0x31, 0x30, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x10, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,

        # DDS_HEADER_DXT10
        0x62, 0x00, 0x00, 0x00, # dxgiFormat: DXGI_FORMAT_BC7_UNORM
        0x03, 0x00, 0x00, 0x00, # resourceDimension: D3D10_RESOURCE_DIMENSION_TEXTURE2D
        0x00, 0x00, 0x00, 0x00, # miscFlag
        0x01, 0x00, 0x00, 0x00, # arraySize: 1
        0x00, 0x00, 0x00, 0x00  # miscFlags2: DDS_ALPHA_MODE_UNKNOWN
    ]
    )

    header[12:16] = height.to_bytes(4, "little", signed=False)
    header[16:20] = width.to_bytes(4, "little", signed=False)
    header[20:24] = width.to_bytes(4, "little", signed=False)
    return header

def bc72dds(im_data, height, width, out_name):
    with open(out_name, "wb") as f:
        dds_header = get_dds_header(height, width)
        f.write(dds_header)
        f.write(im_data)
    

TILE_ORDER = [
     0,  1,  8,  9,  2,  3, 10, 11,
    16, 17, 24, 25, 18, 19, 26, 27,
     4,  5, 12, 13,  6,  7, 14, 15,
    20, 21, 28, 29, 22, 23, 30, 31,
    32, 33, 40, 41, 34, 35, 42, 43,
    48, 49, 56, 57, 50, 51, 58, 59,
    36, 37, 44, 45, 38, 39, 46, 47,
    52, 53, 60, 61, 54, 55, 62, 63
]

def get_tile_pixel_index(t, x, y, width):
    return ((TILE_ORDER[t] >> 3) + y) * width + ((TILE_ORDER[t] & 7) + x)

def untile(pixel_data, width, height, bytes_per_px):
    untiled = bytearray(len(pixel_data))
    s = 0
    for y in range(0, height, 8):
        for x in range(0, width, 8):
            for t in range(64):
                px_offset = get_tile_pixel_index(t, x, y, width) * bytes_per_px
                untiled[px_offset:px_offset+bytes_per_px] = pixel_data[s:s + bytes_per_px]
                s += bytes_per_px
    
    return untiled

def uncompress_body(in_buf, original_len, extra):
    out_buf = bytearray(original_len)
    in_ptr = 0
    out_ptr = 0
    while (in_ptr < len(in_buf)):
        if extra == 8:
            op = in_buf[in_ptr]
            num = in_buf[in_ptr + 1]
        else:
            i_16 = int.from_bytes(in_buf[in_ptr:in_ptr+2], "little", signed=False)
            op = ((1 << extra) - 1) & i_16
            num = ((-1 << extra) & i_16) >> extra
        if (op):
            cpptr = out_ptr - num - 1
            if op > num + 1:
                for _ in range(op):
                    out_buf[out_ptr] = out_buf[cpptr]
                    cpptr += 1
                    out_ptr += 1
            else:
                out_buf[out_ptr:out_ptr+op] = out_buf[cpptr:cpptr+op]
                out_ptr += op
            out_buf[out_ptr] = in_buf[in_ptr + 2]
            out_ptr += 1
            in_ptr += 3
        else:
            in_ptr += 2
            if num:
                out_buf[out_ptr:out_ptr+num] = in_buf[in_ptr:in_ptr+num]
                out_ptr += num
                in_ptr += num
    return out_buf

def uncompress(compressed_bytes, original_len):
    extra = int.from_bytes(compressed_bytes[0:4], "little", signed=True)

    if extra == 8:
        return uncompress_body(compressed_bytes[4:], original_len, extra)
    
    return compressed_bytes[4:]

def itp2dds(path, is_nis=False):
    out_name = path[:-3] + "dds"
    with open(path, "rb") as f:
        magic = struct.unpack(">I", f.read(4))[0]
        if magic != 0x495450ff: #ITP
            raise Exception("unsupported file format")

        images = []

        while True:
            im_type = f.read(4)
            if im_type == b"":
                break
            im_type = im_type.decode("utf-8")
            im_len = struct.unpack("<I", f.read(4))[0]
            data = f.read(im_len)

            if im_type == "IHDR":
                width = int.from_bytes(data[4:8], "little", signed=False)
                height = int.from_bytes(data[8:12], "little", signed=False)
                version = int.from_bytes(data[24:28], "little", signed=False)
            elif im_type == "IDAT":
                block_count = int.from_bytes(data[12:16], "little", signed=False)
                total_compressed = int.from_bytes(data[16:20], "little", signed=False)
                total_original = int.from_bytes(data[24:28], "little", signed=False)
                dptr = 28
                curr_im = bytearray(total_original)
                rptr = 0
                while dptr < len(data):
                    sz_compressed = int.from_bytes(data[dptr:dptr+4], "little", signed=False)
                    dptr += 4
                    sz_original = int.from_bytes(data[dptr:dptr+4], "little", signed=False)
                    dptr += 4
                    compressed = data[dptr:dptr+sz_compressed]
                    dptr += sz_compressed

                    curr_im[rptr:rptr+sz_original] = uncompress(compressed, sz_original)
                    rptr += sz_original
                images.append(curr_im)
        if is_nis == False:
            # NIS version doesn't require untiling.
            images[0] = untile(images[0], width >> 2, height >> 2, 4*4)
    
        bc72dds(images[0], height, width, out_name)
    

fn = sys.argv[1]
is_nis = sys.argv[2] if len(sys.argv) >= 3 else False
itp2dds(fn, is_nis)

im = Image.open(fn[:-3]+"dds")
im.save(fn[:-3]+"png")