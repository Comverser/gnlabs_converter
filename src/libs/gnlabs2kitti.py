import os
from PIL.Image import new
import cv2
import numpy as np

from .config import ROOT_DIR, front_only


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


def read_calib(calib_data):
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


def lwh2hwl(dimensions):
    # l, w, h -> h, w, l )
    dimensions[0], dimensions[2] = dimensions[2], dimensions[0]
    return dimensions


def velo_points2cam_points(height, loc_velo, velo2cam):
    # kitti 카메라 좌표계는 y축이 바닥을 가리키므로 gnlabs 좌표계의 z축에 높이를 2로 나누어 빼준다: z-h/2
    loc_velo_kitti = loc_velo  # shallow copy
    loc_velo_kitti[2] = loc_velo[2] - height / 2
    loc_velo_kitti = np.concatenate((loc_velo_kitti, np.array([1])), axis=0)
    return loc_velo_kitti @ ((velo2cam).T)  # 위치가 반대이므로 (velo2cam).T 적용


def rz2ry(gnlabs_rz):
    # gnlabs rz (facing along x-axis of lidar coordinate) -> kitti ry (facing along x-axis of camera coordinate)
    ry = -gnlabs_rz - np.pi / 2  # 90 degree
    if ry < -np.pi:
        ry += np.pi
    return ry


def write_label(file, label_list):
    with open(file, "w") as f:
        for label in label_list:
            label = map(str, label)
            label_str = " ".join(label) + "\n"
            f.write(label_str)


def read_label(bbox3d, extrinsic_mat):
    label_list = []

    for old_label in bbox3d:
        new_label = {}
        new_label["name"] = old_label["name"]
        new_label["extra"] = "0.00 0 -10 0 0 0 0"  # cls, trunc, occlusion, alpha, bbox
        new_label["dimensions"] = lwh2hwl(old_label["dimensions"])
        height = new_label["dimensions"][0]
        new_loc = velo_points2cam_points(height, old_label["location"], extrinsic_mat)
        new_label["location"] = np.round(new_loc, 2).tolist()
        new_label["rotation_z"] = np.round(rz2ry(old_label["rotation_z"]), 2)

        single_label = []
        for value in new_label.values():
            if isinstance(value, list):
                for elem in value:
                    single_label.append(elem)
            else:
                single_label.append(value)

        if front_only:
            if new_label["location"][2] > 0:  # z-axis is front
                label_list.append(single_label)
        else:
            label_list.append(single_label)

    return label_list
