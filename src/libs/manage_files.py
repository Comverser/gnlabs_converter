import os
import glob

from .config import ROOT_DIR
from .convert_format import convert_dict
from .validation import val_file_names


def gen_out_files(files):
    out_files = []
    for file in files:
        basename = os.path.basename(file)
        out_folder = "out"
        new_file = os.path.join(ROOT_DIR, out_folder, basename)
        out_files.append(new_file)
    return out_files


def gen_files_dict(root_path):
    files_dict = {}
    for ext in convert_dict:
        files = glob.glob(os.path.join(root_path, "**", f"*.{ext}"), recursive=True)
        files.sort()
        files_dict[ext] = files

        out_files = f"out_{ext}"
        files_dict[out_files] = gen_out_files(files)

    val_file_names(files_dict)

    return files_dict
