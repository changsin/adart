import glob
import json
import os
import zipfile
from pathlib import Path

import cv2
import streamlit as st
import streamlit_javascript as st_js
from PIL import Image

from .constants import SUPPORTED_IMAGE_FILE_EXTENSIONS

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


def get_dimension(filename: str) -> (int, int):
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


def load_images(data_files, size: tuple = (100, 100)):
    images = []
    for filename in data_files:
        img = cv2.imread(filename)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, size)  # Resize the image to desired dimensions
        images.append(img)
    return images


def get_window_size():
    window_width = st_js.st_javascript("window.outerWidth")
    window_height = st_js.st_javascript("window.outerHeight")
    return window_width, window_height


def get_dict_value(meta_data_dict: dict, search_str: str):
    cur_dict = meta_data_dict
    level_name_tokens = search_str.split('/')
    for token in level_name_tokens:
        if isinstance(cur_dict, list):
            cur_dict = cur_dict[0].get(token)
        else:
            cur_dict = cur_dict.get(token)

    return cur_dict


# Function to zip a folder
def zip_folder(folder_path, zip_filename):
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname)