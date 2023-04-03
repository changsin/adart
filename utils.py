import os
import json


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
    full_path = os.path.join(folder, filename)
    with open(full_path, 'w', encoding="utf-8") as json_file:
        json_file.write(data)
