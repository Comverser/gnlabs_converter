import sys, os

from libs.convert_format import convert_dict
from libs.th_handler import th_run, empty_files
from libs.logger import error_checker
from libs.manage_files import (
    gen_files_dict,
    gen_image_sets,
    rename_first_set,
    rmdir_input,
    unzip_files,
)
from libs.config import is_remained, max_workers, IN_DIR


def main():

    # parser = argparse.ArgumentParser(description="Convert gnlabs to kitti")
    # parser.add_argument("--num_threads", help="no of thread.", type=int, default=3)
    # args = parser.parse_args()
    if not os.path.exists(IN_DIR):
        print("No input folder")
        sys.exit()

    # print("Unzipping...")
    # unzip_files()

    print("validating and structuring data...")
    files_dict, kitti_folders, files_length = gen_files_dict()

    if error_checker():
        print("######################################")
        print("#---------[conversion error]---------#")
        print("######################################")
        print("Please check gnlabs_converter_error.log file")
        ans = ""
        while not ans in ["yes", "Yes", "YES", "y"]:
            print("Press y to finish...")
            ans = input(">>> ")
        sys.exit()

    for ext, convert_func in convert_dict.items():

        print(f"{ext} converting... ({max_workers} workers)")

        th_run(
            (ext, convert_func),
            files_dict,
            max_workers,
        )
        # empty files generated

        if error_checker():
            print("######################################")
            print("#---------[conversion error]---------#")
            print("######################################")
            print("Please check gnlabs_converter_error.log file")
            ans = ""
            while not ans in ["yes", "Yes", "YES", "y"]:
                print("Press y to finish...")
                ans = input(">>> ")
            break

    # # rename first dataset if 0 index file is missing
    # rename_first_set(empty_files, files_dict)

    # make imageSets files
    gen_image_sets(kitti_folders, files_length, empty_files)

    if not error_checker():
        print(
            f"-----conversion of {files_length} files ({len(empty_files)} empty files removed) has been finished-----"
        )

    if not is_remained:
        rmdir_input(files_dict)
        print("input data has been deleted")


if __name__ == "__main__":
    main()
