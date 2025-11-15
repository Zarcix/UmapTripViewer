from photo_handler.photo_metadata_handler import PhotoMetadataHandler, Metadata
from folium.plugins import BeautifyIcon
from collections import defaultdict

import argparse
import os
import re
import folium

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
    metadata_by_folder: dict[str, list[Metadata]] = {}
    for folder, files in folder_files.items():
        metadata_by_folder[folder] = photoHandler.grab_metadata(files)

    generic_map = folium.Map([0, 0], min_zoom=3, zoom_start=3)
    generic_group = folium.FeatureGroup("All Days", show=False).add_to(generic_map)

    for folder, file_metadata in metadata_by_folder.items():
        folder_group = folium.FeatureGroup(folder, show=False).add_to(generic_map)

        # Group all GPS coordinates together first
        gps_groups = defaultdict(list)
        for idx, metadata in enumerate(file_metadata):
            gps_groups[tuple(metadata.GPS)].append((idx, metadata))

        # Create markers based on the GPS groups
        photo_counter = 0
        for metadata in file_metadata:
            photoIcon = BeautifyIcon(
                border_color="#00ABDC",
                text_color="#00ABDC",
                number=photo_counter,
                inner_icon_style="margin-top:0;",
            )
            folium.Marker(metadata.GPS, popup=metadata.Path, icon=photoIcon).add_to(
                folder_group
            )
            folium.Marker(metadata.GPS, popup=metadata.Path).add_to(generic_group)
            photo_counter += 1

    folium.LayerControl().add_to(generic_map)

    generic_map.show_in_browser()


if __name__ == "__main__":
    main()
