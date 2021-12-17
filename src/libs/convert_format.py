from PIL import Image
import numpy as np
from pypcd import pypcd
import json

from .gnlabs2kitti import write_calib, read_calib, write_label, read_label
from .link import link, cal_bbox2d, cal_bbox3d
from .link import check_link, show_img


def to_png(old_file, new_file):
    img = Image.open(old_file)
    png = img.save(new_file, format="PNG", compress_level=0, interlace=False)
    img.close()


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


def to_kitti(old_file, new_file, new_calib):
    with open(old_file, "r", encoding="UTF8") as calib_file:
        calib_data = json.load(calib_file)
    camera_mat, extrinsic_mat = read_calib(calib_data)

    # # hard coding for calibration
    # camera_mat = np.array([[1350, 0, 960, 0], [0, 1350, 555, 0], [0, 0, 1, 0]])
    # extrinsic_mat = np.array(
    #     [
    #         [-0.07551544, -0.9969779, 0.01823421, 0.1],
    #         [0.05073041, -0.022104, -0.99846775, 1.07],
    #         [0.99585332, -0.07447471, 0.05224629, 1.1],
    #     ]
    # )

    bbox2d = cal_bbox2d(calib_data["bbox2d"])
    bbox3d = cal_bbox3d(calib_data["bbox3d"], camera_mat, extrinsic_mat)
    bbox3d = link(bbox2d, bbox3d)
    label_list = read_label(bbox3d, extrinsic_mat)

    write_calib(new_calib, camera_mat, extrinsic_mat)
    empty_file = write_label(new_file, label_list)

    return empty_file


convert_dict = {"json": to_kitti, "pcd": to_bin, "jpg": to_png}
