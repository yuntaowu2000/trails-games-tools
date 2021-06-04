from PIL import Image
import sys

filename = sys.argv[1]

img = Image.open(filename)

out = img.resize((1280, 720))

out.save("out_{0}".format(filename))