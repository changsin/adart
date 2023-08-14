from abc import ABC


class BaseWriter(ABC):
    def __init__(self):
        self.data_labels_dict = {}

    def write(self, data_labels_dict: dict, filename: dict) -> dict:
        pass
