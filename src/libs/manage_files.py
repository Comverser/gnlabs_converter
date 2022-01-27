import os
import glob
from pathlib import Path
from zipfile import ZipFile
from tqdm import tqdm

from .config import (
    IN_DIR,
    ROOT_DIR,
    OUT_DIR,
    TOP_FOLDER_NAME,
    has_shuffled,
)
from .convert_format import convert_dict
from .validation import val_file_names
from .logger import log_err, log_debug, log_info

shuffled_num_list = []
train_list = []
val_list = []
test_list = []


def rename_first_set(empty_files_not_sorted, files_dict):
    # This function is not working as it doesn't update the ImageSets.
    # rename first dataset if 0 index file is missing
    fname_zero_idx = "000000"
    empty_files = sorted(empty_files_not_sorted)

    if not empty_files:
        log_info.info(f"No empty file input")
        return
    elif empty_files[0].stem != fname_zero_idx:
        log_info.info(f"file number of {fname_zero_idx} exists")
        return

    new_files_list = [files for (ext, files) in files_dict.items() if ("new_" in ext)]

    empty_files_str = [str(empty_file) for empty_file in empty_files]

    first_files = []
    for new_files in new_files_list:
        non_empty_new_files = [
            file for file in new_files if Path(file).stem not in empty_files_str
        ]
        non_empty_new_files.sort()
        first_files.append(non_empty_new_files[0])

    for first_file in first_files:
        first_file_dir = os.path.dirname(first_file)
        first_file_ext = Path(first_file).suffix
        renamed_file = os.path.join(first_file_dir, f"{fname_zero_idx}{first_file_ext}")
        os.rename(first_file, renamed_file)
        log_info.info(f"{first_file} renamed to number of {fname_zero_idx}")


def unzip_files():
    zip_files = glob.glob(os.path.join(ROOT_DIR, IN_DIR, "**", "*.zip"), recursive=True)
    for zip_file in zip_files:
        with ZipFile(zip_file, "r") as zip_ref:
            for file in tqdm(
                iterable=zip_ref.namelist(), total=len(zip_ref.namelist())
            ):

                zip_ref.extract(member=file, path=IN_DIR)


def rmdir_input(files_dict):
    empty_folders = []
    for ext, files in files_dict.items():
        if "new_" not in ext and files:
            # samples some files as references to remove empty folders
            sampling = list(range(0, len(files), 10))
            for n in sampling:
                dirname = os.path.dirname(files[n])
                if dirname not in empty_folders:
                    empty_folders.append(dirname)

    for empty_folder in empty_folders:
        if empty_folder == IN_DIR:
            continue
        else:
            parent = os.path.dirname(empty_folder)

        while True:
            if parent in IN_DIR and parent != IN_DIR:
                break

            if parent not in empty_folders:
                empty_folders.append(parent)

            parent = os.path.dirname(parent)

    empty_folders.sort(reverse=True)
    for empty_folder in empty_folders:
        try:
            os.rmdir(empty_folder)
        except Exception as e:
            log_debug.debug(
                f"cannot remove {empty_folder} as it isn't empty or doesn't exist: {e}"
            )


def mkdir_kitti():
    if not os.path.exists(OUT_DIR):
        os.makedirs(OUT_DIR)
    kitti_struc = {
        "top": TOP_FOLDER_NAME,
        "lv_1": ["ImageSets", "testing", "training"],
        "testing": ["calib", "image_2", "velodyne", "label_2"],
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
    testing_label_2_dir = os.path.join(testing_dir, kitti_struc["testing"][3])

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
    folders.append(testing_label_2_dir)
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
        "testing": [
            testing_calib_dir,
            testing_image_2_dir,
            testing_velodyne_dir,
            testing_label_2_dir,
        ],
        "training": [
            training_calib_dir,
            training_image_2_dir,
            training_velodyne_dir,
            training_label_2_dir,
        ],
    }

    return kitti_folders


def gen_image_sets(kitti_folders, files_length, empty_files):
    empty_file_no = [int(str(i)) for i in empty_files]

    train_list_not_empty = [n for n in train_list if (n not in empty_file_no)]
    val_list_not_empty = [n for n in val_list if (n not in empty_file_no)]
    test_list_not_empty = [n for n in test_list if (n not in empty_file_no)]

    image_sets_dir = kitti_folders["lv_1"][0]

    trainval_txt = os.path.join(image_sets_dir, "trainval.txt")
    train_txt = os.path.join(image_sets_dir, "train.txt")
    val_txt = os.path.join(image_sets_dir, "val.txt")
    test_txt = os.path.join(image_sets_dir, "test.txt")

    # validation
    if (
        len(train_list_not_empty) + len(val_list_not_empty) + len(test_list_not_empty)
    ) != (files_length - len(empty_files)):
        log_err.error("Invalid image_sets")

    with open(trainval_txt, "w") as f:
        for i in train_list_not_empty + val_list_not_empty:
            file_num_str = str(i).zfill(6)
            f.write(f"{file_num_str}\n")

    with open(train_txt, "w") as f:
        for i in train_list_not_empty:
            file_num_str = str(i).zfill(6)
            f.write(f"{file_num_str}\n")

    with open(val_txt, "w") as f:
        for i in val_list_not_empty:
            file_num_str = str(i).zfill(6)
            f.write(f"{file_num_str}\n")

    with open(test_txt, "w") as f:
        for i in test_list_not_empty:
            file_num_str = str(i).zfill(6)
            f.write(f"{file_num_str}\n")


def update_shuffled_num_list(files_length):
    import random

    global shuffled_num_list

    shuffled_num_list = list(range(files_length))
    random.shuffle(shuffled_num_list)


def train_test_split(data, ext, kitti_folders):
    if ext == "jpg":
        if data == "Test":
            out_folder = kitti_folders["testing"][1]
        else:
            out_folder = kitti_folders["training"][1]
        new_ext = "png"
    elif ext == "pcd":
        if data == "Test":
            out_folder = kitti_folders["testing"][2]
        else:
            out_folder = kitti_folders["training"][2]
        new_ext = "bin"
    elif ext == "json":
        if data == "Test":
            out_folder = kitti_folders["testing"][3]
        else:
            out_folder = kitti_folders["training"][3]
        new_ext = "txt"
    elif ext == "new_calib":
        if data == "Test":
            out_folder = kitti_folders["testing"][0]
        else:
            out_folder = kitti_folders["training"][0]
        new_ext = "txt"
    else:
        log_err.error("Unknown format")
    return out_folder, new_ext


def gen_files_kitti(files, ext, kitti_folders):
    # files must be sorted in advance
    out_files = []

    # generate shuffled num list
    if has_shuffled and (not shuffled_num_list):
        update_shuffled_num_list(len(files))

    try:
        for file in files:

            if has_shuffled:
                idx = files.index(file)
                file_num = shuffled_num_list[idx]
            else:
                file_num = files.index(file)
            file_num_str = str(file_num).zfill(6)

            # train and test split
            if "Training" in file:
                out_folder, new_ext = train_test_split("Training", ext, kitti_folders)
                if ext == "json":
                    train_list.append(file_num)
            elif "Validation" in file:
                out_folder, new_ext = train_test_split("Validation", ext, kitti_folders)
                if ext == "json":
                    val_list.append(file_num)
            elif "Test" in file:
                out_folder, new_ext = train_test_split("Test", ext, kitti_folders)
                if ext == "json":
                    test_list.append(file_num)

            new_basename = f"{file_num_str}.{new_ext}"
            new_file = os.path.join(out_folder, new_basename)
            out_files.append(new_file)
    except Exception as e:
        log_err.error(f"Please check input files: {e}")

    return out_files


def gen_files_dict():
    # make folders
    kitti_folders = mkdir_kitti()

    # make new files
    files_dict = {}
    for ext in convert_dict:
        files = glob.glob(
            os.path.join(ROOT_DIR, IN_DIR, "**", f"*.{ext}"), recursive=True
        )
        # files += glob.glob(os.path.join(path, '**',  '*.someting'), recursive=True)
        files.sort()
        files_dict[ext] = files

        new_files = f"new_{ext}"
        files_dict[new_files] = gen_files_kitti(files, ext, kitti_folders)

        if ext == "json":
            new_files = "new_calib"
            files_dict[new_files] = gen_files_kitti(files, new_files, kitti_folders)

    val_file_names(files_dict)

    ext = "json"

    return files_dict, kitti_folders, len(files_dict[ext])
