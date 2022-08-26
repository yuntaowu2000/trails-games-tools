from PIL import Image
import sys

f = sys.argv[1]
im = Image.open(f)
im = im.transpose(Image.FLIP_TOP_BOTTOM)
im.save(f[:-3] + "png")