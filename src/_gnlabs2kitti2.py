import numpy as np
import cv2
import json ###### 모듈 추가#####
import glob #######모듈 추가#####
import os   #######모듈 추가#####

P2 = "1400 0 929 0 0 1400 575 0 0 0 1 0" 

def load_velo2cam():
    euler_angles = np.array([1.18582257, -1.21161618, 1.28073032])
    rotation = cv2.Rodrigues(euler_angles)[0]
    translation = np.array(
        [[0.1], [1.27], [1.4]]
    )
    return np.concatenate((rotation, translation), axis=1)   # (r|t)

##########초기 calib###########
# P2 = "1.407991371000e+03 0 960 0 0 1.407991371000e+03 540 0 0 0 1 0" 

# def load_velo2cam():
#     euler_angles = np.array([1.15572257, -1.22161618, 1.24873032])
#     rotation = cv2.Rodrigues(euler_angles)[0]
#     translation = np.array(
#         [[0.04], [1.233898990000e00], [1.351976560000e00]]
#     )
#     return np.concatenate((rotation, translation), axis=1)  # (r|t)

#####추가 yy#########
def load_velo2cam2(gn_rotation, translation):
    rotation = cv2.Rodrigues(gn_rotation)[0]
    return np.concatenate((rotation, translation), axis=1)  # (r|t)

def load_gnlabs():
    dim = np.array([5.21, 2.28, 1.94])
    loc = np.array([6.45, -0.32, 1.07, 1])
    rz = np.array([2.91])
    return dim, loc, rz


def lwh2hwl(dimensions):
    # l, w, h -> h, w, l )
    dimensions[0], dimensions[2] = dimensions[2], dimensions[0]
    return dimensions


def velo_points2cam_points(height, loc_velo, velo2cam):
    # kitti 카메라 좌표계는 y축이 바닥을 가리키므로 gnlabs 좌표계의 z축에 높이를 2로 나누어 빼준다: z-h/2
    loc_velo_kitti = loc_velo
    loc_velo_kitti[2] = loc_velo[2] - height / 2
    return loc_velo_kitti @ ((velo2cam).T)  # 위치가 반대이므로 (velo2cam).T 적용

#########추가 yy###########
def velo_points2cam_points2(height, loc_velo, velo2cam):
    # kitti 카메라 좌표계는 y축이 바닥을 가리키므로 gnlabs 좌표계의 z축에 높이를 2로 나누어 빼준다: z-h/2
    loc_velo_kitti = loc_velo
    loc_velo_kitti[2] = loc_velo[2] - height / 2
    add_one = np.array([1])
    loc_velo_kitti = np.concatenate((loc_velo, add_one), axis=0)
    return loc_velo_kitti @ ((velo2cam).T)  # 위치가 반대이므로 (velo2cam).T 적용

def rz2ry(gnlabs_rz):
    # gnlabs rz (facing along x-axis of lidar coordinate) -> kitti ry (facing along x-axis of camera coordinate)
    ry = -gnlabs_rz - np.pi / 2  # 90 degree
    if ry < -np.pi:
        ry += np.pi
    return ry


def gnlabs2kitti(p_dim, p_loc, p_rz, velo2cam):
    dim = lwh2hwl(p_dim)
    loc = velo_points2cam_points(p_dim[2], p_loc, velo2cam)
    ry = rz2ry(p_rz)
    return dim, loc, ry



#############추가 yy##########
def load_json(file_path):
    file_list = glob.glob(os.path.join(file_path, '**', '*.json'), recursive=True)
    return file_list
    

def write_label(file, labels):
    # if len(labels) > 1:
    #     labels = np.concatenate(labels)

    # labels = [round(num, 2) for num in labels]
    txt_file_name = "./label_2/{:s}.txt".format(file)
    with open(txt_file_name , "w") as f:
        for label in labels:
            label = map(str, label)
            label_str = " ".join(label) + "\n"
            f.write(label_str)

###########추가############
def write_calib(file_name, extrinsic, P2):
    extrinsic_matrix=extrinsic.reshape(1,12)
    extrinsic_matrix=extrinsic_matrix.tolist()
    extri_str=' '.join(str(e) for e in extrinsic_matrix[0])
    extri_str="Tr_velo_to_cam: "+extri_str+ "\n"
    P2_str="P2: "+P2+"\n"
    f = open("./sample.txt", 'r')
    lines = f.readlines()
    edited_lines=""
    for line in lines:
        if 'P2:' in line:
            edited_lines += P2_str
        elif 'Tr_velo_to_cam:' in line:
            edited_lines += extri_str
        else:
            edited_lines += line
    f.close()
    txt_file_name = "./calib/{:s}.txt".format(file_name)
    with open(txt_file_name, "w") as f:
        edited_lines = map(str, edited_lines)
        edited_lines = "".join(edited_lines)
        f.write(edited_lines)



#############추가 yy##########
def json_info(file_list): 
    num_files=len(file_list)
    #json 파일 하나만 읽어서 적용
    for i in range(0, num_files):
        file = file_list[i]
        file_path = os.path.splitext(file)[0]
        file_name = file_path.split('/')[-1]
        with open(file, 'r', encoding='UTF8') as data_file:
            data = json.load(data_file)
        #calib 에 필요한 정보 (intrinsic, rotation, translation)
        intrinsic=data["calib"]["intrinsic"]
        rotation=data["calib"]["rotation"]
        translation=data["calib"]["translation"]
        #label 에 필요한 정보 (bbox3d)
        #bbox2d=data["bbox2d"]
        rotation=np.array(rotation)
        translation=np.array(translation).reshape(3,1)
        extrinsic_matrix=load_velo2cam()
        write_calib(file_name, extrinsic_matrix, P2)
    #######label###########
        bbox3d=data["bbox3d"]
        label = []
        default=['0 0 -10 0 0 0 0']
        for j in range(0, len(bbox3d)):
            bbox3d[j]["dimensions"]=lwh2hwl(bbox3d[j]["dimensions"])
            bbox3d[j]["location"]=np.round(velo_points2cam_points2(bbox3d[j]["dimensions"][0],bbox3d[j]["location"],extrinsic_matrix),2)
            bbox3d[j]["location"]=bbox3d[j]["location"].tolist()
            bbox3d[j]["rotation_z"]=np.round(rz2ry(bbox3d[j]["rotation_z"]),2)
            single_list = []
            single_dict = bbox3d[j]
            if single_dict['location'][2]>0:          ########추가###########
                single_list.append(single_dict['name'])
                single_list.append(default[0])
                single_list.append(single_dict['dimensions'][0])
                single_list.append(single_dict['dimensions'][1])
                single_list.append(single_dict['dimensions'][2])
                single_list.append(single_dict['location'][0])
                single_list.append(single_dict['location'][1])
                single_list.append(single_dict['location'][2])
                single_list.append(single_dict['rotation_z'])
                label.append(single_list)
                write_label(file_name, label)
          


if __name__ == "__main__":
    # input - yy
    #velo2cam = load_velo2cam()
    #label_in = load_gnlabs()
    json_path="./gnict_data/"
    file_list=load_json(json_path)

    json_info(file_list)

    # output - hs
    #label_out = gnlabs2kitti(*label_in, velo2cam)

    #print("velo2cam:\n", velo2cam)
    #print("label:\n", label_out)
