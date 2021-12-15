import numpy as np

# def isRotationMatrix(R):
#     Rt = np.transpose(R)
#     shouldBeIdentity = np.dot(Rt, R)
#     I = np.identity(3, dtype=R.dtype)
#     n = np.linalg.norm(I - shouldBeIdentity)
#     return n < 1e-6


# import math
# def rotationMatrixToEulerAngles(R):
#     assert isRotationMatrix(R)
#     sy = math.sqrt(R[0, 0] * R[0, 0] + R[1, 0] * R[1, 0])
#     singular = sy < 1e-6
#     if not singular:
#         x = math.atan2(R[2, 1], R[2, 2])
#         y = math.atan2(-R[2, 0], sy)
#         z = math.atan2(R[1, 0], R[0, 0])
#     else:
#         x = math.atan2(-R[1, 2], R[1, 1])
#         y = math.atan2(-R[2, 0], sy)
#         z = 0
#     return np.array([x, y, z])


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
    rotMat1 = np.dot(Rz_yaw, np.dot(Ry_pitch, Rx_roll))
    rotMat2 = (Rz_yaw @ Ry_pitch) @ Rx_roll

    return rotMat1, rotMat2


if __name__ == "__main__":
    result1, result2 = euler_to_rotMat(-0.95819537, -1.49156157, 2.54664635)
    print(result1)
    print(result2)
