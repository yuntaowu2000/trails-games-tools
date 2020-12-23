from PIL import Image
import sys
import os

filename = sys.argv[1]
im = Image.open(filename)
imgwidth, imgheight = im.size


result = im.crop((411, 144, 1500, 1045))

if (not os.path.exists("output")):
    os.makedirs("output")

result.save("output\{0}".format(filename))
