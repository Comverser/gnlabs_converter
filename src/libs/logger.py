import logging
import os

from .config import ROOT_DIR


def setup_logger(name, log_file, level=logging.DEBUG):
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


info_path = os.path.join(ROOT_DIR, "gnlabs_converter_info.log")
debug_path = os.path.join(ROOT_DIR, "gnlabs_converter_debug.log")
err_path = os.path.join(ROOT_DIR, "gnlabs_converter_error.log")

log_info = setup_logger("info", info_path)
log_debug = setup_logger("debug", debug_path)
log_err = setup_logger("error", err_path)


def error_checker():
    if os.stat(err_path).st_size != 0:
        return "Error. Check the log for more information."
