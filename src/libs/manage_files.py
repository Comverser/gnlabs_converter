import os
import glob

from .config import OUT_DIR, has_shuffled
from .convert_format import convert_dict
from .validation import val_file_names
from .logger import log_err

shuffled_num_list = []


def mkdir_kitti():
    kitti_struc = {
        "top": "out_kitti_format",
        "lv_1": ["ImageSets", "testing", "training"],
        "testing": ["calib", "image_2", "velodyne"],
        "training": ["calib", "image_2", "velodyne", "label_2"],
    }

    folders = []

    top_dir = os.path.join(OUT_DIR, kitti_struc["top"])

    image_sets_dir = os.path.join(top_dir, kitti_struc["lv_1"][0])
    testing_dir = os.path.join(top_dir, kitti_struc["lv_1"][1])
    training_dir = os.path.join(top_dir, kitti_struc["lv_1"][2])

    testing_calib_dir = os.path.join(testing_dir, kitti_struc["testing"][0])
    testing_image_2_dir = os.path.join(testing_dir, kitti_struc["testing"][1])
    testing_velodyne_dir = os.path.join(testing_dir, kitti_struc["testing"][2])

    training_calib_dir = os.path.join(training_dir, kitti_struc["training"][0])
    training_image_2_dir = os.path.join(training_dir, kitti_struc["training"][1])
    training_velodyne_dir = os.path.join(training_dir, kitti_struc["training"][2])
    training_label_2_dir = os.path.join(training_dir, kitti_struc["training"][3])

    folders.append(top_dir)
    folders.append(image_sets_dir)
    folders.append(testing_dir)
    folders.append(testing_calib_dir)
    folders.append(testing_image_2_dir)
    folders.append(testing_velodyne_dir)
    folders.append(training_dir)
    folders.append(training_calib_dir)
    folders.append(training_image_2_dir)
    folders.append(training_velodyne_dir)
    folders.append(training_label_2_dir)

    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)

    kitti_folders = {
        "lv_1": [image_sets_dir, testing_dir, training_dir],
        "testing": [testing_calib_dir, testing_image_2_dir, testing_velodyne_dir],
        "training": [
            training_calib_dir,
            training_image_2_dir,
            training_velodyne_dir,
            training_label_2_dir,
        ],
    }

    return kitti_folders


def gen_files_kitti(files, ext, folders):
    # generate shuffled num list
    global shuffled_num_list
    if has_shuffled and (not shuffled_num_list):
        import random

        files_length = len(files)
        shuffled_num_list = list(range(files_length))
        random.shuffle(shuffled_num_list)

    # files must be sorted in advance
    out_files = []

    if ext == "jpg":
        out_folder = folders["training"][1]
        new_ext = "png"
    elif ext == "pcd":
        out_folder = folders["training"][2]
        new_ext = "bin"
    elif ext == "json":
        out_folder = folders["training"][3]
        new_ext = "txt"
    else:
        log_err.error("Unknown format")

    for file in files:
        if has_shuffled:
            idx = files.index(file)
            file_num = shuffled_num_list[idx]
        else:
            file_num = files.index(file)
        new_basename = f"{str(file_num).zfill(6)}.{new_ext}"
        new_file = os.path.join(out_folder, new_basename)
        out_files.append(new_file)

    return out_files


def gen_files_dict(root_path):
    # make folders
    folders = mkdir_kitti()

    # make new files
    files_dict = {}
    for ext in convert_dict:
        files = glob.glob(os.path.join(root_path, "**", f"*.{ext}"), recursive=True)
        files.sort()
        files_dict[ext] = files

        new_files = f"new_{ext}"
        files_dict[new_files] = gen_files_kitti(files, ext, folders)

    val_file_names(files_dict)

    return files_dict
