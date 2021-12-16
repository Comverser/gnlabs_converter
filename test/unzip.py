from zipfile import ZipFile
from tqdm import tqdm
import glob
import os
import concurrent.futures

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
IN_DIR = ROOT_DIR


# def unzip_files():
#     zip_files = glob.glob(os.path.join(ROOT_DIR, "**", "*.zip"), recursive=True)
#     for zip_file in zip_files:
#         with ZipFile(zip_file, "r") as zip_ref:
#             for file in tqdm(
#                 iterable=zip_ref.namelist(), total=len(zip_ref.namelist())
#             ):

#                 zip_ref.extract(member=file, path=IN_DIR)


def unzip(file):
    zf.extract(file, path=IN_DIR)


if __name__ == "__main__":
    zip_files = glob.glob(os.path.join(ROOT_DIR, "**", "*.zip"), recursive=True)

    for zip_file in tqdm(zip_files):
        with concurrent.futures.ProcessPoolExecutor() as executor:
            zf = ZipFile(zip_file)
            executor.map(unzip, zf.infolist())
