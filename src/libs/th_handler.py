import threading
from tqdm import tqdm
import os
from pathlib import Path

from .logger import log_info, log_err
from .utils import reset_total, updtotal
from .config import is_remained, has_removed_empty

empty_files = []


def th_func(convert_dict, files_dict, a, b, num_files):
    global empty_files
    ext, convert_func = convert_dict
    for i in tqdm(range(a, b)):
        old_file = files_dict[ext][i]
        new_file = files_dict[f"new_{ext}"][i]
        try:
            if ext == "json":
                new_calib = files_dict["new_calib"][i]
                empty_file = convert_func(old_file, new_file, new_calib)
                if empty_file and has_removed_empty:
                    empty_files.append(empty_file)
            else:
                new_file_name = os.path.basename(new_file)
                new_file_name_wo_ext = Path(new_file_name).with_suffix("")
                if new_file_name_wo_ext not in empty_files:
                    convert_func(old_file, new_file)

            if not is_remained:
                os.remove(old_file)
            log_info.info(f"Completed {old_file} ({str(updtotal())}/{str(num_files)})")
        except Exception as e:
            log_err.error(
                f"Error on {old_file} ({str(updtotal())}/{str(num_files)}): {e}"
            )


def th_run(convert_dict, files_dict, num_threads):
    ext, _ = convert_dict
    log_info.info(f"Conversion start")

    num_files = len(files_dict[ext])

    files_per_thread = num_files // num_threads
    remainder_files = num_files % num_threads
    threads = []

    for i in range(0, num_threads):
        a = i * files_per_thread
        b = a + files_per_thread

        if i == num_threads - 1:
            b += remainder_files

        thread = threading.Thread(
            None,
            th_func,
            "Thread " + str(i),
            (convert_dict, files_dict, a, b, num_files),
            {},
        )
        threads.append(thread)
        thread.start()
        # log_debug.debug("Created Thread " + str(i))

    for i in range(0, num_threads):
        threads[i].join()
        # log_debug.debug("Joined Thread " + str(i))

    reset_total()
