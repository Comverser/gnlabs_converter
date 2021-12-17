import os
import glob
import numpy as np
import json
import math
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.patches as patches

dist_critical = 300


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


def read_calib(calib_data):
    # camera matrix
    intrinsic = np.array(calib_data["calib"]["intrinsic"]).astype(int)
    cam_offset = np.array([[0], [0], [0]])
    camera_mat = np.concatenate((intrinsic, cam_offset), axis=1)
    euler_angles = np.array(calib_data["calib"]["rotation"])
    rotation = euler_to_rotMat(*euler_angles)
    translation = np.array(calib_data["calib"]["translation"]).reshape(3, 1)
    extrinsic_mat = np.concatenate((rotation, translation), axis=1)
    return camera_mat, extrinsic_mat


def draw_bbox2d(label2d):
    # extract 2d info
    xmin = label2d["bbox"][0]
    ymin = label2d["bbox"][1]
    xmax = label2d["bbox"][2]
    ymax = label2d["bbox"][3]
    width = xmax - xmin
    height = ymax - ymin

    patch_rect = patches.Rectangle(
        (xmin, ymin),
        width,
        height,
        edgecolor="r",
        facecolor="none",
    )

    return patch_rect


def check_link(jpg_file, label2d, label3d):
    img = mpimg.imread(jpg_file)
    _, ax = plt.subplots(1)
    ax.imshow(img)

    # draw center point of 2d bbox
    ax.plot(*label2d["center"], "or")
    # draw bbox of 2d label
    ax.add_patch(draw_bbox2d(label2d))
    # draw center point of cuboid
    ax.plot(*label3d["cam_pos"], "og")

    plt.show()


def show_img(jpg_file, bbox2d, bbox3d):
    img = mpimg.imread(jpg_file)
    _, ax = plt.subplots(1)
    ax.imshow(img)

    for label2d in bbox2d:
        # draw center point of 2d bbox
        ax.plot(*label2d["center"], "or")
        # draw bbox of 2d label
        ax.add_patch(draw_bbox2d(label2d))

    for label3d in bbox3d:
        if label3d["cam_pos"] and label3d["bbox"] != [0, 0, 0, 0]:
            # draw center point of cuboid
            ax.plot(*label3d["cam_pos"], "og")

    plt.show()


def cal_bbox2d(bbox2d):
    for label in bbox2d:
        xmin = label["bbox"][0]
        ymin = label["bbox"][1]
        xmax = label["bbox"][2]
        ymax = label["bbox"][3]
        x_center = (xmin + xmax) / 2
        y_center = (ymin + ymax) / 2
        label["center"] = x_center, y_center
        label["occlusion"] = 0 if label["occluded"] == False else 1
        label["area"] = (xmax - xmin) * (ymax - ymin)

    # prioritize
    bbox2d = sorted(bbox2d, key=lambda d: d["area"], reverse=True)
    bbox2d = sorted(bbox2d, key=lambda d: d["occlusion"])

    return bbox2d


def velo_point2cam_point(loc_velo, velo2cam):
    loc_velo_1 = np.concatenate((loc_velo, np.array([1])), axis=0)
    return velo2cam @ loc_velo_1


def cam_3d_to_2d(cam3d_point, camera_mat_kitti):
    if cam3d_point[2] < 0:
        return None

    camera_mat = camera_mat_kitti[:, :3]
    cam3d_point /= cam3d_point[2]
    cam2d_point = camera_mat @ cam3d_point

    return cam2d_point[:2].tolist()


def cal_bbox3d(bbox3d, camera_mat, extrinsic_mat):
    for label in bbox3d:
        label["cam_loc"] = velo_point2cam_point(label["location"], extrinsic_mat)
        cam_loc_temp = label["cam_loc"]
        # label["cam_pos"] is None if not in range
        label["cam_pos"] = cam_3d_to_2d(cam_loc_temp, camera_mat)
        label["occlusion"] = 0

        if label["cam_loc"][2] > 0:
            dist3d_x = label["cam_loc"][0]
            dist3d_z = label["cam_loc"][2]
            label["alpha"] = math.atan(dist3d_x / dist3d_z)  # type float
        else:
            label["alpha"] = -10

        label["bbox"] = [0, 0, 0, 0]
    return bbox3d


def read_label(bbox3d, extrinsic_mat):
    for old_label in bbox3d:
        new_label = {}  # insertion order is important
        new_label["extra"] = "0.00 0 -10"  # trunc, occlusion, alpha
        new_label["bbox"] = "0 0 0 0"


cls_3d_to_2d = {
    "Car": ["Car", "Van", "Other Vehicle"],
    "Cycle": ["Motorbike", "Bicycle", "Electric Scooter"],
    "Pedestrian": ["Adult", "Child"],
}


def link(bbox2d, bbox3d, jpg_file=None):
    result3d = []
    for label2d in bbox2d:
        tmp_dist = dist_critical
        target_lb3d = None
        # only 3d labels in camera viewport
        for label3d in (bbox3d for bbox3d in bbox3d if bbox3d["cam_pos"]):
            # check class name and duplication
            if (label2d["name"] in cls_3d_to_2d[label3d["name"]]) and (
                label3d not in result3d
            ):
                p1 = label2d["center"]
                p2 = label3d["cam_pos"]
                dist = math.dist(p1, p2)

                dist3d_x = label3d["cam_loc"][0]
                dist3d_y = label3d["cam_loc"][1]
                dist3d_z = label3d["cam_loc"][2]
                dist3d = np.sqrt(dist3d_x ** 2 + dist3d_y ** 2 + dist3d_z ** 2)

                moving_crit_dist = dist_critical * 10 / dist3d

                if dist < tmp_dist and dist < moving_crit_dist:
                    tmp_dist = dist
                    target_lb3d = label3d

        if target_lb3d:
            check_link(jpg_file, label2d, target_lb3d)

            idx3d = bbox3d.index(target_lb3d)
            label3d = bbox3d[idx3d]
            label3d["occlusion"] = label2d["occlusion"]  # type int
            label3d["bbox"] = [int(n) for n in label2d["bbox"]]

            result3d.append(target_lb3d)

    return bbox3d


if __name__ == "__main__":
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    json_files = glob.glob(os.path.join(ROOT_DIR, "**", "*.json"), recursive=True)
    jpg_files = glob.glob(os.path.join(ROOT_DIR, "**", "*.jpg"), recursive=True)
    json_files.sort()
    jpg_files.sort()

    num = 0

    json_file = json_files[num]
    jpg_file = jpg_files[num]

    with open(json_file, "r", encoding="UTF8") as calib_file:
        calib_data = json.load(calib_file)

    camera_mat, extrinsic_mat = read_calib(calib_data)
    bbox2d = cal_bbox2d(calib_data["bbox2d"])
    bbox3d = cal_bbox3d(calib_data["bbox3d"], camera_mat, extrinsic_mat)
    bbox3d = link(bbox2d, bbox3d, jpg_file)
    read_label(bbox3d, extrinsic_mat)

    show_img(jpg_file, bbox2d, bbox3d)
