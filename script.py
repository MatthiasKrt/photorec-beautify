import os
import shutil
import mimetypes
import sys
from datetime import datetime

try:
    import exifread
    EXIFREAD_AVAILABLE = True
except ImportError:
    EXIFREAD_AVAILABLE = False
    print("Warning: The module 'exifread' is not installed. EXIF data cannot be read.", file=sys.stderr)

def get_file_type(file_path):
    """ Determines the file type based on MIME type detection. """
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type:
        return mime_type.split("/")[0]  # image, video, audio, etc.
    return "unknown"

def get_new_filename(file_path):
    """ Attempts to rename a file based on its metadata. """
    file_type = get_file_type(file_path)
    timestamp = os.path.getmtime(file_path)
    
    if file_type == "image" and EXIFREAD_AVAILABLE:
        with open(file_path, 'rb') as f:
            tags = exifread.process_file(f, stop_tag="DateTimeOriginal")
            if "EXIF DateTimeOriginal" in tags:
                date_str = str(tags["EXIF DateTimeOriginal"]).replace(':', '-').replace(' ', '_')
                return datetime.strptime(date_str, "%Y-%m-%d_%H-%M-%S")
    
    # Fallback: Use file creation date
    return datetime.fromtimestamp(timestamp)

def sort_and_rename_photorec_output(input_dir, output_dir):
    """ Sorts and renames files recovered by Photorec into the desired structure. """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.lower() == 'report.xml':
                continue  # Skip report.xml files
            
            file_path = os.path.join(root, file)
            file_type = get_file_type(file_path)
            date = get_new_filename(file_path)
            
            year = date.strftime("%Y")
            month = date.strftime("%m")
            new_name = date.strftime("%Y-%m-%d_%H-%M-%S") + os.path.splitext(file_path)[1]
            
            type_dir = os.path.join(output_dir, file_type, year, month)
            if not os.path.exists(type_dir):
                os.makedirs(type_dir)
            
            new_path = os.path.join(type_dir, new_name)
            shutil.copy2(file_path, new_path)
            print(f"Copied: {file_path} -> {new_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <input_directory> <output_directory>")
        sys.exit(1)
    
    input_directory = sys.argv[1]  # Get input directory from command line argument
    output_directory = sys.argv[2]  # Get output directory from command line argument
    
    sort_and_rename_photorec_output(input_directory, output_directory)
