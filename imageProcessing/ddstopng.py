from wand.image import Image
import sys

filename = sys.argv[1]
finished_file = filename[:-3] + "png"
with Image(filename=filename) as img:
    img.flip()
    img.save(filename=finished_file)