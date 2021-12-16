from zipfile import ZipFile
from tqdm import tqdm
import multiprocessing as mp
import glob
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
IN_DIR = ROOT_DIR


def unzip_file(zip_file):
    with ZipFile(zip_file, "r") as zip_ref:
        for file in tqdm(iterable=zip_ref.namelist(), total=len(zip_ref.namelist())):
            zip_ref.extract(member=file, path=IN_DIR)


def fanout_unzip(zip_files):
    pool = mp.Pool(min(mp.cpu_count(), len(zip_files)))  # number of workers
    pool.map(unzip_file, zip_files, chunksize=2)
    pool.close()


if __name__ == "__main__":
    zip_files = glob.glob(os.path.join(ROOT_DIR, "**", "*.zip"), recursive=True)
    fanout_unzip(zip_files)
    # some image seems to be not decompressed properly... so I don't use multiprocessing for unzip
