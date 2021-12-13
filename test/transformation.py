import numpy as np

# velo (0,0,0) camera (1,2,3)

# velo_points (5,6,7)
velo_points = np.array([5, 6, 7])

translation = np.array([1, 2, 3])  # velo 기준
translation2 = np.array([1, -3, 2])  # camera 기준

roll = 1.5708

Rx_roll = np.array(
    [[1, 0, 0], [0, np.cos(roll), -np.sin(roll)], [0, np.sin(roll), np.cos(roll)]]
)

cam_points = np.dot((velo_points + translation), (Rx_roll).T)
print(cam_points)

velo_points = np.array([5, 6, 7, 1])
Rx_roll_trans = np.array(
    [
        [1, 0, 0, 1],
        [0, np.cos(roll), -np.sin(roll), -3],
        [0, np.sin(roll), np.cos(roll), 2],
    ]
)
cam_points2 = np.dot((velo_points), (Rx_roll_trans).T)
print(cam_points2)
