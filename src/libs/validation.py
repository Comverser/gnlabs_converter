import os
from pathlib import Path
from tqdm import tqdm
from .logger import log_err


def file_name_list(files_dict):
    files_values = []
    i = 0
    for values in tqdm(files_dict.values()):
        temp = []
        if i == 0:
            for path in values:
                file = os.path.basename(path)
                file_wo_ext = Path(file).with_suffix("")
                files_values.append(file_wo_ext)
        else:
            for path in values:
                file = os.path.basename(path)
                file_wo_ext = Path(file).with_suffix("")
                temp.append(file_wo_ext)
            if temp != files_values:
                log_err.error("Input data names are not matched")
        i += 1
