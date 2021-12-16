from libs.convert_format import convert_dict
from libs.th_handler import th_run, empty_files
from libs.logger import error_checker
from libs.manage_files import gen_files_dict, gen_image_sets, rmdir_input, unzip_files
from libs.config import is_remained, max_workers


def main():

    # parser = argparse.ArgumentParser(description="Convert gnlabs to kitti")
    # parser.add_argument("--num_threads", help="no of thread.", type=int, default=3)
    # args = parser.parse_args()

    print("Unzipping...")
    unzip_files()

    print("validating and structuring data...")
    files_dict, folders, files_length = gen_files_dict()

    for ext, convert_func in convert_dict.items():

        print(f"{ext} converting... ({max_workers} workers)")

        th_run(
            (ext, convert_func),
            files_dict,
            max_workers,
        )

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

    # make imageSets files
    gen_image_sets(folders, files_length, empty_files)

    if not error_checker():
        print(
            f"-----conversion of {files_length} files ({len(empty_files)} empty files) has been finished-----"
        )

    if not is_remained:
        rmdir_input(files_dict)
        print("input data has been deleted")


if __name__ == "__main__":
    main()
