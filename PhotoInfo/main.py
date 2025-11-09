import argparse
import exiftool
import os

def args():
    parser = argparse.ArgumentParser()
    parser.add_argument("file_location", help="A folder to all the files")
    args = parser.parse_args()
    assert args.file_location
    return args.file_location

def get_files(folder):
    
    pass

def main():
    folder = args()
    get_files(folder)

if __name__ == "__main__":
    main()