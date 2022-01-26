import numpy as np
import os
from pathlib import Path

from .config import front_only, has_removed_empty


def euler_to_rotMat(roll, pitch, yaw):  # rx, ry, rz axis of lidar coordinates
    Rz_yaw = np.array(
        [[np.cos(yaw), -np.sin(yaw), 0], [np.sin(yaw), np.cos(yaw), 0], [0, 0, 1]]
    )
    Ry_pitch = np.array(
        [
            [np.cos(pitch), 0, np.sin(pitch)],
            [0, 1, 0],
            [-np.sin(pitch), 0, np.cos(pitch)],
        ]
    )
    Rx_roll = np.array(
        [[1, 0, 0], [0, np.cos(roll), -np.sin(roll)], [0, np.sin(roll), np.cos(roll)]]
    )
    # R = RzRyRx
    rotMat = np.dot(Rz_yaw, np.dot(Ry_pitch, Rx_roll))
    return rotMat


def write_calib(new_calib, camera_mat, extrinsic_mat):
    # camera mat
    camera_mat_list = camera_mat.reshape(-1).tolist()
    camera_mat_str = " ".join(str(elem) for elem in camera_mat_list)

    # extrinsic mat
    extrinsic_mat_list = extrinsic_mat.reshape(-1).tolist()
    extrinsic_mat_str = " ".join(str(elem) for elem in extrinsic_mat_list)

    with open(new_calib, "w") as f:
        f.write("P0: 0 0 0 0 0 0 0 0 0 0 0 0\n")
        f.write("P1: 0 0 0 0 0 0 0 0 0 0 0 0\n")
        f.write(f"P2: {camera_mat_str}\n")
        f.write("P3: 0 0 0 0 0 0 0 0 0 0 0 0\n")
        f.write("R0_rect: 1 0 0 0 1 0 0 0 1\n")
        f.write(f"Tr_velo_to_cam: {extrinsic_mat_str}\n")
        f.write("Tr_imu_to_velo: 0 0 0 0 0 0 0 0 0 0 0 0")


def read_calib(calib_data):
    # camera matrix
    intrinsic = np.array(calib_data["calib"]["intrinsic"]).astype(int)
    cam_offset = np.array([[0], [0], [0]])
    camera_mat = np.concatenate((intrinsic, cam_offset), axis=1)
    # extrinsic matrix (r|t)
    # rod_vector = np.array(calib_data["calib"]["rotation"])
    # rotation = cv2.Rodrigues(rod_vector)[0]
    euler_angles = np.array(calib_data["calib"]["rotation"])
    rotation = euler_to_rotMat(*euler_angles)
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
    return loc_velo_kitti @ ((velo2cam).T)


def rz2ry(gnlabs_rz):
    # gnlabs rz (facing along x-axis of lidar coordinate) -> kitti ry (facing along x-axis of camera coordinate)
    ry = -gnlabs_rz - np.pi / 2  # 90 degree
    if ry < -np.pi:
        ry += np.pi
    return ry


def write_label(file, label_list):
    if label_list or not has_removed_empty:
        with open(file, "w") as f:
            for label in label_list:
                label = [f"{x:.2f}" if type(x) is float else str(x) for x in label]

                label_str = " ".join(label) + "\n"
                f.write(label_str)
        return None
    else:
        file = os.path.basename(file)
        file_wo_ext = Path(file).with_suffix("")
        return file_wo_ext


def rename_class(old_cls):
    if old_cls == "Car":
        new_cls = "Car"
    elif old_cls == "Cycle":
        new_cls = "Cyclist"
    elif old_cls == "Pedestrian":
        new_cls = "Pedestrian"
    return new_cls


def read_label(bbox3d, extrinsic_mat):
    label_list = []

    for old_label in bbox3d:
        new_label = {}  # insertion order is important
        new_label["name"] = rename_class(old_label["name"])
        new_label["truncation"] = old_label["truncation"]
        new_label["occlusion"] = old_label["occlusion"]
        new_label["alpha"] = old_label["alpha"]
        if old_label["bbox"] == [0, 0, 0, 0]:
            return label_list
        new_label["bbox"] = old_label["bbox"]
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
