import argparse

# gui
from easygui import msgbox

# custom
from config import ROOT_DIR
from libs import th_handler
from libs import converter_func
from libs import logger


def main():
    parser = argparse.ArgumentParser(description="Convert gnlabs to kitti")
    parser.add_argument("--root_path", help="root path.", type=str, default=ROOT_DIR)
    parser.add_argument("--num_threads", help="no of thread.", type=int, default=3)
    args = parser.parse_args()

    for key in converter_func.dict:
        print(
            f"{converter_func.dict[key][1]} converting... ({args.num_threads} workers)"
        )

        th_handler.run(
            converter_func.dict[key],
            args.root_path,
            args.num_threads,
        )

        if logger.error_checker():
            print(f"{converter_func.dict[key][1]} conversion error!")
            msgbox(logger.error_checker())
        else:
            print(f"{converter_func.dict[key][1]} conversion has been finished")
            print("----------------------------------------")


if __name__ == "__main__":
    main()
