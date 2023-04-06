import glob
import json
import os

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


def from_file(str_default, folder, filename):
    full_path = os.path.join(folder, filename)
    if os.path.exists(full_path) and os.path.getsize(full_path) > 0:
        file = open(full_path, 'r', encoding='utf-8')
        return json.load(file)

    return json.loads(str_default)


def to_file(data, folder, filename):
    """
    save data to path
    """
    if not os.path.exists(folder):
        os.mkdir(folder)

    full_path = os.path.join(folder, filename)
    with open(full_path, 'w', encoding="utf-8") as json_file:
        json_file.write(data)


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
                    file_info_to_display[sub_folder] = file_info_to_display[sub_folder] + len(matched)
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
