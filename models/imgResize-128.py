# resize model image textures so that max(width, height)=128 and keeps the ratio
from PIL import Image
import sys

filename = sys.argv[1]

img = Image.open(filename)
img_height = img.height
img_width = img.width

if img_width == img_height:
    out = img.resize((128, 128))
    out.save(filename)
elif img_height > img_width:
    out = img.resize((int(128 / img_height * img_width), 128))
    out.save(filename)
else:
    out = img.resize((128, int(128 / img_width * img_height)))
    out.save(filename)