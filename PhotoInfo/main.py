from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

import argparse
import exiftool
import os
import glob

et = exiftool.ExifToolHelper()

def args():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", help="A folder to all the files")
    args = parser.parse_args()
    assert args.directory
    return args.directory

def get_all_files(directory):
    pattern = os.path.join(directory, "**", "*")
    all_files = glob.glob(pattern, recursive=True)
    files = [f for f in all_files if os.path.isfile(f)]
    return files

def grab_metadata(files):
    def __parse_metadata(metadata):
        dt = metadata.get("EXIF:DateTimeOriginal") or metadata.get("QuickTime:CreateDate")
        ofs = metadata.get("EXIF:OffsetTimeDigitized") or "+00:00"

        # Skip invalid EXIF cases
        if not dt:
            metadata["ParsedDate"] = None
            return metadata

        dt = dt.replace("T", " ").replace("Z", "")
        combined = f"{dt}{ofs}"

        try:
            local_dt = datetime.strptime(combined, "%Y:%m:%d %H:%M:%S%z")
            utc_dt = local_dt.astimezone(timezone.utc)
            metadata["ParsedDate"] = utc_dt
        except Exception:
            metadata["ParsedDate"] = None

        return metadata

    metadatas = et.get_metadata(files)
    with ThreadPoolExecutor(max_workers=8) as executor:
        metadatas = list(executor.map(__parse_metadata, metadatas))
    
    metadatas = sorted(
        metadatas,
        key=lambda m: m.get("ParsedDate") or datetime.min.replace(tzinfo=timezone.utc)
    )

    filtered = [
        {
            "ParsedDate": m.get("ParsedDate"),
            "GPS": m.get("Composite:GPSPosition"),
            "Path": m.get("SourceFile"),
        }
        for m in metadatas
    ]

    return filtered

def main():
    directory = args()
    all_files = get_all_files(directory)
    sorted_file_data = grab_metadata(all_files)
    breakpoint()

if __name__ == "__main__":
    main()