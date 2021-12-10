import os
from PIL import Image
import numpy as np
from pypcd import pypcd
import json

from .config import is_remained

from .gnlabs2kitti import write_calib, read_calib, write_label, read_label


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


def to_kitti(old_file, new_file, new_calib):
    with open(old_file, "r", encoding="UTF8") as calib_file:
        calib_data = json.load(calib_file)
    camera_mat, extrinsic_mat = read_calib(calib_data)
    write_calib(new_calib, camera_mat, extrinsic_mat)

    label_list = read_label(calib_data["bbox3d"], extrinsic_mat)
    write_label(new_file, label_list)


convert_dict = {"jpg": to_png, "pcd": to_bin, "json": to_kitti}
