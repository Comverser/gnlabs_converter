import numpy as np
import os
import argparse
from pypcd import pypcd
import csv
from tqdm import tqdm
import shutil

current_path = os.path.dirname(os.path.realpath(__file__))


def main():
    parser = argparse.ArgumentParser(description="Convert .pcd to .bin")
    parser.add_argument(
        "--pcd_path",
        help=".pcd file path.",
        type=str,
        default=current_path,
    )
    parser.add_argument(
        "--ascii_path",
        help=".ascii pcd file path.",
        type=str,
        default=current_path,
    )
    parser.add_argument(
        "--bin_path",
        help=".bin file path.",
        type=str,
        default=current_path,
    )
    args = parser.parse_args()

    pcd_files = []
    seq = 0
    for (path, dir, files) in os.walk(args.pcd_path):
        for filename in files:
            ext = os.path.splitext(filename)[-1]
            if ext == ".pcd":
                pcd_files.append(path + "/" + filename)

    pcd_files.sort()

    ## Make ascii_path directory
    try:
        if not (os.path.isdir(args.ascii_path)):
            os.makedirs(os.path.join(args.ascii_path))
    except OSError as e:
        if e.errno != errno.EEXIST:
            print("Failed to create directory!!!!!")
            raise
    ## Make bin_path directory
    try:
        if not (os.path.isdir(args.bin_path)):
            os.makedirs(os.path.join(args.bin_path))
    except OSError as e:
        if e.errno != errno.EEXIST:
            print("Failed to create directory!!!!!")
            raise

    ## Generate csv meta file
    csv_file_path = os.path.join(args.bin_path, "meta.csv")
    csv_file = open(csv_file_path, "w")
    meta_file = csv.writer(
        csv_file, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL
    )
    ## Write csv meta file header
    meta_file.writerow(
        [
            "pcd file name",
            "bin file name",
        ]
    )
    print("Finish to generate csv meta file")

    for pcd_file in tqdm(pcd_files):
        pc = pypcd.PointCloud.from_path(pcd_file)
        ## binary_pcd -> ascii_pcd
        ascii_file_name = "{:06d}.pcd".format(seq)
        pc.save_pcd(ascii_file_name, compression="ascii")

        pc = pypcd.PointCloud.from_path(ascii_file_name)
        ## Generate bin file name
        bin_file_name = "{:06d}.bin".format(seq)
        bin_file_path = os.path.join(args.bin_path, bin_file_name)

        ## Get data from pcd (x, y, z, intensity, ring, time)
        np_x = (np.array(pc.pc_data["x"], dtype=np.float32)).astype(np.float32)
        np_y = (np.array(pc.pc_data["y"], dtype=np.float32)).astype(np.float32)
        np_z = (np.array(pc.pc_data["z"], dtype=np.float32)).astype(np.float32)
        np_i = (np.array(pc.pc_data["intensity"], dtype=np.float32)).astype(
            np.float32
        ) / 256
        # np_r = (np.array(pc.pc_data['ring'], dtype=np.float32)).astype(np.float32)
        # np_t = (np.array(pc.pc_data['time'], dtype=np.float32)).astype(np.float32)

        ## Stack all data
        points_32 = np.transpose(np.vstack((np_x, np_y, np_z, np_i)))

        ## Save bin file
        points_32.tofile(bin_file_path)

        ## Write csv meta file
        meta_file.writerow([os.path.split(pcd_file)[-1], bin_file_name])

        os.remove(ascii_file_name)
        ##shutil.move(ascii_file_name, args.ascii_path +'/'+ ascii_file_name)
        seq = seq + 1


if __name__ == "__main__":
    main()
