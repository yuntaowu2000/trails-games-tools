# for Akatsuki no kiseki only
from PIL import Image
import numpy as np
import sys

filename = sys.argv[1]

im = Image.open(filename)
im_arr = np.array(im)
out_arr = np.zeros((1024, 1920, 4), dtype=np.uint8)

out_arr[:,1918:,:] = 0
if im_arr.shape[0] > 1024:
    # mobile ver
    out_arr[:,:1918,0:3] = im_arr[:1024,:1918,0:3]
    out_arr[:,:1918,3] = (255 * 3 - im_arr[1024:,:1918,0] - im_arr[1024:,:1918,1] - im_arr[1024:,:1918,2]).clip(min=0,max=255)
else:
    # PC ver
    out_arr[:,:1918,0:3] = im_arr[:,:1918,0:3]
    out_arr[:,:1918,3] = 255 - im_arr[:,:1918,3]

im_out = Image.fromarray(out_arr)
im_out.save("out_" + filename[:-4]+".png")