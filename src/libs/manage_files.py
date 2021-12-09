import os
import glob

from .config import ROOT_DIR
from .convert_format import convert_dict
from .validation import val_file_names
from .config import out_base_folder, kitti_structure
from .logger import log_debug


def mkdir_if_not_exist():
    # Check whether the specified path exists or not
    new_dir = os.path.join(ROOT_DIR, out_base_folder)
    isExist = os.path.exists(new_dir)
    if not isExist:
        os.makedirs(new_dir)
        log_debug.debug("The new directory is created!")


def gen_out_files(files):
    out_files = []
    for file in files:
        basename = os.path.basename(file)
        out_folder = out_base_folder
        new_file = os.path.join(ROOT_DIR, out_folder, basename)
        out_files.append(new_file)
    return out_files


def gen_files_dict(root_path):
    files_dict = {}
    for ext in convert_dict:
        files = glob.glob(os.path.join(root_path, "**", f"*.{ext}"), recursive=True)
        files.sort()
        files_dict[ext] = files

        new_files = f"new_{ext}"
        files_dict[new_files] = gen_out_files(files)

    val_file_names(files_dict)
    mkdir_if_not_exist()

    return files_dict
