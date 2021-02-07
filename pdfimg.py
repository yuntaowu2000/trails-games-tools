from typing import Text
import fitz
import time
import re
import os

def pdf2pic(path, pic_path):
    doc = fitz.open(path)                      # 打开pdf文件
    imgcount = 0
    for i in range(len(doc)):
        imglist = doc.getPageImageList(i)
        for j, img in enumerate(imglist):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)   # make pixmap from image
            new_name = "图片{}.png".format(imgcount) # 生成图片的名称
            if pix.n - pix.alpha < 4:      # can be saved as PNG
                pix.writePNG(os.path.join(pic_path, new_name))
            else:                          # CMYK: must convert first
                pix0 = fitz.Pixmap(fitz.csRGB, pix)
                pix0.writePNG(os.path.join(pic_path, new_name))
                pix0 = None                # free Pixmap resources
            pix = None                     # free Pixmap resources
            imgcount += 1

if __name__=='__main__':
    path = r"C:\Users\yunta\Desktop\trails-game\tx_treasure\test\东京迷城ex+攻略.pdf"
    pic_path = r'C:\Users\yunta\Desktop\trails-game\tx_treasure\test'
    pdf2pic(path, pic_path)