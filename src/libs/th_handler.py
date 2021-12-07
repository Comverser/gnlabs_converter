import os
import glob
import threading

from .logger import log_info, log_err
from .utils import reset_total, updtotal


def th_func(converter_func, files, a, b, num_files):
    for i in range(a, b):
        file = files[i]
        try:
            converter_func(file)
            log_info.info(f"Completed {file} ({str(updtotal())}/{str(num_files)})")
        except Exception as e:
            log_err.error(f"Error on {file} ({str(updtotal())}/{str(num_files)}: {e}")


def run(converter_dict, path, num_threads):
    log_info.info(f"Conversion start: {os.path.dirname(os.path.realpath(__file__))}")

    files = glob.glob(
        os.path.join(path, "**", f"*.{converter_dict[1]}"), recursive=True
    )

    num_files = len(files)

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
            (converter_dict[0], files, a, b, num_files),
            {},
        )
        threads.append(thread)
        thread.start()
        log_info.debug("Created Thread " + str(i))

    for i in range(0, num_threads):
        threads[i].join()
        log_info.debug("Joined Thread " + str(i))

    reset_total()
