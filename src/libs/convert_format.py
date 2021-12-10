import os
from PIL import Image
import numpy as np
from pypcd import pypcd
import json
import cv2

from .config import ROOT_DIR, is_remained


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


def write_calib(new_calib, camera_mat, extrinsic_mat):
    # camera mat
    camera_mat_list = camera_mat.reshape(-1).tolist()
    camera_mat_str = " ".join(str(elem) for elem in camera_mat_list)
    camera_mat_str = "P2: " + camera_mat_str + "\n"

    # extrinsic mat
    extrinsic_mat_list = extrinsic_mat.reshape(-1).tolist()
    extrinsic_mat_str = " ".join(str(elem) for elem in extrinsic_mat_list)
    extrinsic_mat_str = "Tr_velo_to_cam: " + extrinsic_mat_str + "\n"

    calib_ref_file = os.path.join(ROOT_DIR, "calib_ref.txt")
    with open(calib_ref_file, "r") as f:
        lines = f.readlines()
        edited_lines = ""
        for line in lines:
            if "P2:" in line:
                edited_lines += camera_mat_str
            elif "Tr_velo_to_cam:" in line:
                edited_lines += extrinsic_mat_str
            else:
                edited_lines += line

    with open(new_calib, "w") as f:
        f.write(edited_lines)


def read_calib(file):
    with open(file, "r", encoding="UTF8") as calib_file:
        calib_data = json.load(calib_file)
    # camera matrix
    intrinsic = np.array(calib_data["calib"]["intrinsic"]).astype(int)
    cam_offset = np.array([[0], [0], [0]])
    camera_mat = np.concatenate((intrinsic, cam_offset), axis=1)
    # extrinsic matrix (r|t)
    rod_vector = np.array(calib_data["calib"]["rotation"])
    rotation = cv2.Rodrigues(rod_vector)[0]
    translation = np.array(calib_data["calib"]["translation"]).reshape(3, 1)
    extrinsic_mat = np.concatenate((rotation, translation), axis=1)
    return camera_mat, extrinsic_mat


def to_kitti(old_file, new_file, new_calib):
    write_calib(new_calib, *read_calib(old_file))


convert_dict = {"jpg": to_png, "pcd": to_bin, "json": to_kitti}
