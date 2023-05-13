import glob
import json
import os
from PIL import Image
from pathlib import Path

from .constants import SUPPORTED_IMAGE_FILE_EXTENSIONS
import streamlit as st

# Convert bytes to a more human-readable format
ONE_K_BYTES = 1024.0


def default(obj):
    if hasattr(obj, 'to_json'):
        return obj.to_json()
    raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')


def humanize_bytes(size):

    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(size) < ONE_K_BYTES:
            return "%3.1f %sB" % (size, unit)
        size /= ONE_K_BYTES


def from_file(filename, default_json="{}"):
    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        file = open(filename, 'r', encoding='utf-8')
        return json.load(file)

    return json.loads(default_json)


def to_file(data, filename):
    """
    save data to path
    """
    with open(filename, 'w', encoding="utf-8") as json_file:
        json_file.write(data)


def glob_files(folder_path, patterns=SUPPORTED_IMAGE_FILE_EXTENSIONS):
    matched = []
    for pattern in patterns:
        globbed = glob.glob(os.path.join(folder_path, '*.' + pattern))
        if globbed:
            matched.extend(globbed)

    return matched


def generate_file_tree(folder_path, patterns):
    file_tree_to_return = {}
    for root, dirs, files in os.walk(folder_path):
        level = root.replace(folder_path, '').count(os.sep)
        indent = '-' * (level)

        file_info_to_display = dict()
        for pattern in patterns:
            matched = glob.glob(os.path.join(root, pattern), recursive=True)
            if matched:
                matched = [os.path.basename(full_path) for full_path in matched]
                sub_folder = root.replace(folder_path, '')
                if file_info_to_display.get(sub_folder):
                    file_info_to_display[sub_folder] += len(matched)
                else:
                    file_info_to_display[sub_folder] = len(matched)

                if file_tree_to_return.get(root):
                    file_tree_to_return[root].extend(matched)
                else:
                    file_tree_to_return[root] = matched
                # for filename in matched:
                #     if not os.path.isdir(filename):
                #         file_tree_to_return.append(os.path.join(root, filename))

        for folder, count in file_info_to_display.items():
            st.markdown('{}📁({}) {}/'.format(indent, count, folder))

    return file_tree_to_return


def step_size(value):
    if value < 10:
        return 1.0
    elif value < 100:
        return 10.0
    elif value < 1000:
        return 100.0
    elif value < 10000:
        return 1000.0
    elif value < 100000:
        return 10000.0
    else:
        return 100.0


def get_resolution(filename: str) -> (int, int):
    with Image.open(filename) as img:
        # Get the width and height of the image
        width, height = img.size

    # width, height = 0, 0
    # # Read the image using opencv-python
    # img = cv2.imread(filename)
    # if img is not None:
    #     # Get the width and height of the image
    #     height, width, _ = img.shape

    return width, height


def from_text_file(text_file):
    return Path(text_file).read_text()
    # if ext.lower() == '.jpg':
    #     with open(filename, 'rb') as f:
    #         # Jump to the start of the frame (SOI marker) and read 4 bytes
    #         f.seek(2)
    #         b = f.read(4)
    #         # Check if it's the start of a frame
    #         assert b == b'\xff\xc0' or b == b'\xff\xc2', "Not a valid JPEG file"
    #         # Read the image height and width from the frame header
    #         return struct.unpack('>HH', f.read(4))
    # elif ext.lower() == 'bmp':
    #     with open(filename, 'rb') as f:
    #         # Jump to the start of the header and read 8 bytes
    #         f.seek(18)
    #         header_data = f.read(8)
    #         # Unpack the width and height from the header
    #         return struct.unpack('<ii', header_data[4:])