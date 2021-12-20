import os
import sys
from pathlib import Path

ROOT_DIR = os.path.abspath(sys.argv[1])

executable_name = os.path.basename(sys.executable)
if "python" not in executable_name:
    executable_path = os.path.dirname(sys.executable)
    SETTING_FILE = Path(os.path.join(executable_path, "settings.ini"))
else:
    file_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    SETTING_FILE = Path(os.path.join(file_path, "settings.ini"))

if SETTING_FILE.is_file():
    import configparser

    config = configparser.ConfigParser()
    config.read(SETTING_FILE)

    # output
    OUT_DIR = os.path.join(ROOT_DIR, config.get("out", "root_folder_name"))
    TOP_FOLDER_NAME = config.get("out", "top_folder_name")
    has_shuffled = config.getboolean("out", "has_shuffled")
    has_removed_empty = config.getboolean("out", "has_removed_empty")
    train_val_ratio = config.getfloat("out", "train_val_ratio")
    front_only = config.getboolean("out", "front_only")
    # input
    is_remained = config.getboolean("in", "is_remained")
    IN_DIR = os.path.join(ROOT_DIR, config.get("in", "root_folder_name"))
    # system
    max_workers = config.getint("sys", "max_workers")
else:
    # output
    OUT_DIR = os.path.join(ROOT_DIR, "data")
    TOP_FOLDER_NAME = "gnlabs"
    has_shuffled = True
    has_removed_empty = True
    train_val_ratio = 0.875
    front_only = True
    # input
    is_remained = False
    IN_DIR = os.path.join(ROOT_DIR, "data")
    # system
    max_workers = 4
