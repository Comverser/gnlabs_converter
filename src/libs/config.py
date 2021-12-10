import os
import sys
from pathlib import Path

ROOT_DIR = os.path.abspath(sys.argv[1])


settings = Path(os.path.join(ROOT_DIR, "settings.ini"))

if settings.is_file():
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
    # system
    num_threads = config.getint("sys", "num_threads")
else:
    # output
    OUT_DIR = os.path.join(ROOT_DIR, "data")
    TOP_FOLDER_NAME = "gnlabs"
    has_shuffled = True
    train_val_ratio = 0.875
    front_only = True
    # input
    is_remained = False
    IN_DIR = os.path.join(ROOT_DIR, "data")
    # system
    num_threads = 10
