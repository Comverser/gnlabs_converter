import logging
import os


def setup_logger(name, log_file, level=logging.DEBUG):
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


log_info = setup_logger("info", "info.log")
log_debug = setup_logger("debug", "debug.log")
log_err = setup_logger("error", "error.log")


def error_checker():
    if os.stat("error.log").st_size != 0:
        return "Error. Check the log for more information."
