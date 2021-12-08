import os
import glob

from .converter_func import convert_dict
from .validation import file_name_list


def gen_files_dict(root_path):
    files_dict = {}
    for key in convert_dict:
        files = glob.glob(os.path.join(root_path, "**", f"*.{key}"), recursive=True)
        files.sort()
        files_dict[key] = files

    file_name_list(files_dict)

    return files_dict
