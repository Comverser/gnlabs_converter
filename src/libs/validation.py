import os
from pathlib import Path
from tqdm import tqdm
from .logger import log_err, log_val, log_debug


def val_file_names(files_dict):
    first_file_list = []
    i = 0
    for ext, files in tqdm(files_dict.items()):
        temp = []
        # first file list as reference
        if i == 0:
            for path in files:
                log_val.info(f"{path}")
                file = os.path.basename(path)
                file_wo_ext = Path(file).with_suffix("")
                first_file_list.append(file_wo_ext)
        # next file list
        else:
            for path in files:
                log_val.info(f"{path}")
                file = os.path.basename(path)
                file_wo_ext = Path(file).with_suffix("")
                temp.append(file_wo_ext)

            if "new_" in ext:
                if len(temp) != len(first_file_list):
                    log_err.error("Output data length are not correct")
            else:
                idx = 0
                for one, cmp in zip(first_file_list, temp):
                    if one != cmp:
                        log_debug.debug(f"{idx}: {one} and {cmp} are not matched")
                    idx += 1
                if temp != first_file_list:
                    log_err.error("Input data names are not matched")

        i += 1
