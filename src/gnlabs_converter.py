import sys

# gui
from easygui import msgbox

# custom
from libs.convert_format import convert_dict
from libs.th_handler import th_run
from libs.logger import error_checker
from libs.manage_files import gen_files_dict, unzip_files, rmdir_input
from libs.config import is_remained, num_threads


def main():

    # parser = argparse.ArgumentParser(description="Convert gnlabs to kitti")
    # parser.add_argument("--num_threads", help="no of thread.", type=int, default=3)
    # args = parser.parse_args()

    print("Unzipping...")
    unzip_files()

    print("validating and structuring data...")
    files_dict = gen_files_dict()

    for ext, convert_func in convert_dict.items():

        print(f"{ext} converting... ({num_threads} workers)")

        th_run(
            (ext, convert_func),
            files_dict,
            num_threads,
        )

        if error_checker():
            print("conversion error!")
            msgbox(error_checker())
            sys.exit()
    print("-----conversion has been finished-----")

    if not is_remained:
        rmdir_input(files_dict)
        print("input data has been deleted")


if __name__ == "__main__":
    main()
