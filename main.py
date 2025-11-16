from photo_handler.photo_metadata_handler import PhotoMetadataHandler, Metadata
from folium.plugins import BeautifyIcon
from collections import defaultdict

import argparse
import os
import re
import folium
import tkinter
from tkinter import filedialog

photoHandler = PhotoMetadataHandler()

VIDEO_MIME_TYPES = {
    "mp4": "video/mp4",
    "mov": "video/quicktime",
    "mkv": "video/x-matroska",
    "webm": "video/webm",
    "avi": "video/x-msvideo",
    "flv": "video/x-flv",
    "wmv": "video/x-ms-wmv",
    "m4v": "video/x-m4v",
    "mpeg": "video/mpeg",
}


def natural_sort(l):
    # Stolen from https://stackoverflow.com/questions/4836710/is-there-a-built-in-function-for-string-natural-sort
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split("([0-9]+)", key)]
    return sorted(l, key=alphanum_key)


def folder_picker():
    root = tkinter.Tk()
    root.withdraw()
    file_path = filedialog.askdirectory()
    return file_path


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
    directory = folder_picker()
    folder_files = get_files_by_folder(directory)
    metadata_by_folder: dict[str, list[Metadata]] = {}
    for folder, files in folder_files.items():
        metadata_by_folder[folder] = photoHandler.grab_metadata(files)

    generic_map = folium.Map([0, 0], min_zoom=3, zoom_start=3)
    # generic_group = folium.FeatureGroup("All Days", show=False).add_to(generic_map)

    for folder, file_metadata in metadata_by_folder.items():
        folder_group = folium.FeatureGroup(folder, show=False).add_to(generic_map)

        # Group all GPS coordinates together first while preserving date order
        gps_groups = defaultdict(list)
        for idx, metadata in enumerate(file_metadata):
            gps_groups[tuple(metadata.GPS)].append((idx, metadata))

        marker_builder = defaultdict(list)

        # Create Popups based on GPS coords
        for coords, metadatas in gps_groups.items():
            html = (
                f"<div style='min-width: 15vw;'>"
                f"<h1>Long Lat: {coords}</h1>"
                f"<h1>Images in this location:</h1>"
                f"</div>"
            )
            for index, metadata in metadatas:
                # We'll let the browser handle rendering the pictures instead of loading them all here
                html += f"<details><summary style='font-size: 1.5em; font-weight: bold'>Index {index}</summary>"
                file_extension = metadata.Path.lower().rsplit(".", 1)[-1]
                html += f"<div><a href='{metadata.Path}' target='_blank'>File Location</a></div>"
                if ext := VIDEO_MIME_TYPES.get(file_extension):
                    html += f"<video controls style='max-height: 15vw; max-width: 10vw; object-fit: contain;'><source src='{metadata.Path}' type='{ext}'></video>"
                else:
                    html += f"<img src='{metadata.Path}' style='max-height: 15vw; max-width: 10vw; object-fit: contain;'></details>"
                html += "\n"
            marker_builder[coords].append(
                folium.Popup(html, max_width="500%", lazy=True)
            )

        # Create Icons based on GPS coords
        for coords, metadatas in gps_groups.items():
            ranges = []
            indexes = [m[0] for m in metadatas]
            start = prev = indexes[0]

            for n in indexes[1:]:
                if n != prev + 1:
                    ranges.append(f"{start}-{prev}" if start != prev else str(start))
                    start = n
                prev = n

            ranges.append(f"{start}-{prev}" if start != prev else str(start))
            marker_builder[coords].append(", ".join(ranges))

        for coord, marker_info in marker_builder.items():
            folium.Marker(coord, popup=marker_info[0], tooltip=marker_info[1]).add_to(
                folder_group
            )

    folium.LayerControl().add_to(generic_map)

    generic_map.show_in_browser()


if __name__ == "__main__":
    main()
