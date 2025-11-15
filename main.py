import argparse
import os
import glob
import folium
import re

from photo_handler.photo_metadata_handler import PhotoMetadataHandler

photoHandler = PhotoMetadataHandler()


def natural_sort(l):
    # Stolen from https://stackoverflow.com/questions/4836710/is-there-a-built-in-function-for-string-natural-sort
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split("([0-9]+)", key)]
    return sorted(l, key=alphanum_key)


def args():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", help="A folder to all the files")
    args = parser.parse_args()
    assert args.directory
    return args.directory


def get_files_by_folder(root_dir):
    result = {}

    # Iterate only the first level of folders
    top_level_folders = natural_sort(
        [e for e in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, e))]
    )

    for folder_name in top_level_folders:
        folder_path = os.path.join(root_dir, folder_name)
        files = []

        for dirpath, _, filenames in os.walk(folder_path):
            for fname in filenames:
                files.append(os.path.join(dirpath, fname))

        result[folder_name] = files

    return result


def main():
    directory = args()
    folder_files = get_files_by_folder(directory)
    metadata_by_folder = {}
    for folder, files in folder_files.items():
        metadata_by_folder[folder] = photoHandler.grab_metadata(files)

    breakpoint()

    genericMap = folium.Map([0, 0], min_zoom=3, zoom_start=3)

    genericMap.show_in_browser()


if __name__ == "__main__":
    main()
