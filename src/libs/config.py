import os
import sys
from pathlib import Path

from .logger import log_debug

_ = os.path.abspath(sys.argv[0])
ROOT_DIR = os.path.dirname(_)

settings = Path(os.path.join(ROOT_DIR, "settings.ini"))

if settings.is_file():
    log_debug.debug("settings are loaded from settings.ini file")
    import configparser

    config = configparser.ConfigParser()
    config.read(os.path.join(ROOT_DIR, "settings.ini"))

    # output
    OUT_DIR = os.path.join(ROOT_DIR, config.get("out", "root_folder_name"))
    TOP_FOLDER_NAME = config.get("out", "top_folder_name")
    has_shuffled = config.getboolean("out", "has_shuffled")
    train_val_ratio = config.getfloat("out", "train_val_ratio")
    front_only = config.getboolean("out", "front_only")
    # input
    is_remained = config.getboolean("in", "is_remained")
    IN_DIR = os.path.join(ROOT_DIR, config.get("in", "root_folder_name"))
else:
    log_debug.debug("settings are loaded from default values")
    # output
    OUT_DIR = os.path.join(ROOT_DIR, "data")
    TOP_FOLDER_NAME = "gnlabs"
    has_shuffled = True
    train_val_ratio = 0.875
    front_only = True
    # input
    is_remained = False
    IN_DIR = os.path.join(ROOT_DIR, "data")
