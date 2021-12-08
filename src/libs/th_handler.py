import threading
from tqdm import tqdm

from .logger import log_info, log_err, log_debug
from .utils import reset_total, updtotal


def th_func(converter_func, files, a, b, num_files):
    for i in tqdm(range(a, b)):
        file = files[i]
        try:
            converter_func(file)
            log_info.info(f"Completed {file} ({str(updtotal())}/{str(num_files)})")
        except Exception as e:
            log_err.error(f"Error on {file} ({str(updtotal())}/{str(num_files)}: {e}")


def run(dict_item, files, num_threads):
    log_info.info(f"Conversion start")

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
            (dict_item[1], files, a, b, num_files),
            {},
        )
        threads.append(thread)
        thread.start()
        log_debug.debug("Created Thread " + str(i))

    for i in range(0, num_threads):
        threads[i].join()
        log_debug.debug("Joined Thread " + str(i))

    reset_total()
