import os
from PIL import Image
import numpy as np
from pypcd import pypcd

from .config import is_remained


def to_png(old_file, new_file):
    img = Image.open(old_file)
    png = img.save(new_file, format="PNG", compress_level=0, interlace=False)
    img.close()
    if not is_remained:
        os.remove(old_file)


def to_bin(old_file, new_file):
    pc = pypcd.PointCloud.from_path(old_file)

    ## Get data from pcd (x, y, z, intensity)
    np_x = (np.array(pc.pc_data["x"], dtype=np.float32)).astype(np.float32)
    np_y = (np.array(pc.pc_data["y"], dtype=np.float32)).astype(np.float32)
    np_z = (np.array(pc.pc_data["z"], dtype=np.float32)).astype(np.float32)
    np_i = (np.array(pc.pc_data["intensity"], dtype=np.float32)).astype(
        np.float32
    ) / 256

    ## Stack all data
    points_32 = np.transpose(np.vstack((np_x, np_y, np_z, np_i)))

    ## Save bin old_file
    points_32.tofile(new_file)

    if not is_remained:
        os.remove(old_file)


def to_kitti(old_file, new_file):
    pass


convert_dict = {"jpg": to_png, "pcd": to_bin, "json": to_kitti}
