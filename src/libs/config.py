import os
import sys
import configparser

_ = os.path.abspath(sys.argv[0])
ROOT_DIR = os.path.dirname(_)

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
