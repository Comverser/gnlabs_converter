import os

from PIL import Image

from .utils import print


def to_png(file):
    out = file.replace(".jpg", ".png")
    img = Image.open(file)
    png = img.save(out, format="PNG", compress_level=0, interlace=False)
    img.close()
    os.remove(file)


def to_bin(file):
    print(file)


dict = {"jpg": [to_png, "jpg"], "pcd": [to_bin, "pcd"]}
