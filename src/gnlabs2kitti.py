import numpy as np
import cv2


def load_velo2cam():
    euler_angles = np.array([1.15572257, -1.22161618, 1.24873032])
    rotation = cv2.Rodrigues(euler_angles)[0]
    translation = np.array(
        [[8.620100000000e-01], [1.233898990000e00], [-1.351976560000e00]]
    )
    return np.concatenate((rotation, translation), axis=1)  # (r|t)


def load_gnlabs():
    dim = np.array([5.21, 2.28, 1.94])
    loc = np.array([6.45, -0.32, 1.07, 1])
    rz = np.array([2.91])
    return dim, loc, rz


def lwh2hwl(dimensions):
    # l, w, h -> h, w, l
    dimensions[0], dimensions[2] = dimensions[2], dimensions[0]
    return dimensions


def velo_points2cam_points(height, loc_velo, velo2cam):
    # kitti 카메라 좌표계는 y축이 바닥을 가리키므로 gnlabs 좌표계의 z축에 높이를 2로 나누어 빼준다: z-h/2
    loc_velo_kitti = loc_velo
    loc_velo_kitti[2] = loc_velo[2] - height / 2
    return loc_velo_kitti @ ((velo2cam).T)  # 위치가 반대이므로 (velo2cam).T 적용


def rz2ry(gnlabs_rz):
    # gnlabs rz (facing along x-axis of lidar coordinate) -> kitti ry (facing along x-axis of camera coordinate)
    ry = -gnlabs_rz - np.pi / 2  # 90 degree
    if ry < -np.pi:
        ry += np.pi
    return ry


def to_kitti(p_dim, p_loc, p_rz, velo2cam):
    dim = lwh2hwl(p_dim)
    loc = velo_points2cam_points(p_dim[2], p_loc, velo2cam)
    ry = rz2ry(p_rz)
    return dim, loc, ry


def write_label(file, labels):
    if len(labels) > 1:
        labels = np.concatenate(labels)

    labels = [round(num, 2) for num in labels]

    with open(file, "w") as f:
        labels = map(str, labels)
        f.write(" ".join(labels))


if __name__ == "__main__":
    velo2cam = load_velo2cam()
    label_in = load_gnlabs()
    label_out = to_kitti(*label_in, velo2cam)
    file = "/home/s/dev/gnlabs_converter/sample.txt"
    write_label(file, label_out)

    # print("velo2cam:\n", velo2cam)
    # print("label:\n", label_out)
