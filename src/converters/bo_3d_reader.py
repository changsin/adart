from src.common.utils import from_file
from .base_reader import BaseReader


class BO3DReader(BaseReader):

    def parse(self, label_files, data_files=None):
        super().parse(label_files, data_files)

        for label_file in label_files:
            labels_dict = from_file(label_file)

