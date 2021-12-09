import os

_ = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(_))
OUT_DIR = ROOT_DIR

is_remained = True
has_shuffled = True
train_val_ratio = 0.875


# import sys
# current_path = os.path.dirname(sys.executable)
