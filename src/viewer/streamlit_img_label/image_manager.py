import os

import numpy as np
from PIL import Image

from src.models.dart_labels import DartLabels
from src.viewer.streamlit_img_label.annotation import output_xml

"""
.. module:: streamlit_img_label
   :synopsis: manage.
.. moduleauthor:: Changsin Lee
"""


class DartImageManager:
    """ImageManager
    Manage the image object.

    Args:
        filename(str): the image file.
    """

    def __init__(self, image_folder, image_labels: DartLabels.Image):
        """initiate module"""
        self.image_lables = image_labels
        # TODO: setting it as a place holder - to be removed later
        self._label_filename = image_folder
        self._img = Image.open(os.path.join(image_folder, image_labels.name))
        self._rects = []
        self._load_rects()
        self._resized_ratio_w = 1
        self._resized_ratio_h = 1

    def get_img(self):
        """get the image object

        Returns:
            img(PIL.Image): the image object.
        """
        return self._img

    def _load_rects(self):
        converted_rects = []
        for label_object in self.image_lables.objects:
            rect = dict()
            left, top, right, bottom = label_object.points
            width = right - left
            height = bottom - top
            rect["left"] = int(left)
            rect["top"] = int(top)
            rect["width"] = int(width)
            rect["height"] = int(height)
            rect["label"] = label_object.label
            rect["shapeType"] = "rectangle"

            converted_rects.append(rect)

        self._rects = converted_rects

    def get_rects(self):
        """get the rects

        Returns:
            rects(list): the bounding boxes of the image.
        """
        return self._rects

    def resizing_img(self, max_height=1000, max_width=1000):
        """resizing the image by max_height and max_width.

        Args:
            max_height(int): the max_height of the frame.
            max_width(int): the max_width of the frame.
        Returns:
            resized_img(PIL.Image): the resized image.
        """
        resized_img = self._img.copy()
        if resized_img.height > max_height:
            ratio = max_height / resized_img.height
            resized_img = resized_img.resize(
                (int(resized_img.width * ratio), int(resized_img.height * ratio))
            )
        if resized_img.width > max_width:
            ratio = max_width / resized_img.width
            resized_img = resized_img.resize(
                (int(resized_img.width * ratio), int(resized_img.height * ratio))
            )

        self._resized_ratio_w = self._img.width / resized_img.width
        self._resized_ratio_h = self._img.height / resized_img.height
        return resized_img

    def _resize_rect(self, rect):
        resized_rect = {}
        resized_rect["left"] = rect["left"] / self._resized_ratio_w
        resized_rect["width"] = rect["width"] / self._resized_ratio_w
        resized_rect["top"] = rect["top"] / self._resized_ratio_h
        resized_rect["height"] = rect["height"] / self._resized_ratio_h
        if "label" in rect:
            resized_rect["label"] = rect["label"]
        resized_rect["shapeType"] = "rectangle"
        return resized_rect

    def get_resized_rects(self):
        """get resized the rects according to the resized image.

        Returns:
            resized_rects(list): the resized bounding boxes of the image.
        """
        return [self._resize_rect(rect) for rect in self._rects]

    def _chop_box_img(self, rect):
        rect["left"] = int(rect["left"] * self._resized_ratio_w)
        rect["width"] = int(rect["width"] * self._resized_ratio_w)
        rect["top"] = int(rect["top"] * self._resized_ratio_h)
        rect["height"] = int(rect["height"] * self._resized_ratio_h)
        left, top, width, height, label, shapeType = (
            rect["left"],
            rect["top"],
            rect["width"],
            rect["height"],
            rect["label"],
            rect["shapeType"]
        )

        raw_image = np.asarray(self._img).astype("uint8")
        prev_img = np.zeros(raw_image.shape, dtype="uint8")
        prev_img[top : top + height, left : left + width] = raw_image[
            top : top + height, left : left + width
        ]
        prev_img = prev_img[top : top + height, left : left + width]
        label = ""
        if "label" in rect:
            label = rect["label"]
        return (Image.fromarray(prev_img), label)

    def init_annotation(self, rects):
        """init annotation for current rects.

        Args:
            rects(list): the bounding boxes of the image.
        Returns:
            prev_img(list): list of preview images with default label.
        """
        self._current_rects = rects
        return [self._chop_box_img(rect) for rect in self._current_rects]

    def set_annotation(self, index, label):
        """set the label of the image.

        Args:
            index(int): the index of the list of bounding boxes of the image.
            label(str): the label of the bounding box
        """
        self._current_rects[index]["label"] = label

    def save_annotation(self):
        """output the xml annotation file."""
        output_xml(self._label_filename, self._img, self._current_rects)


class DartImageDirManager:
    def __init__(self, img_dir_name, dart_labels: DartLabels):
        self._img_dir_name = img_dir_name
        self._img_files = [image.name for image in dart_labels.images]

        # TODO: to be removed later
        self._annotation_dir_name = img_dir_name
        self._annotations_files = []

    def get_all_img_files(self, allow_types=["png", "jpg", "jpeg"]):
        return self._img_files

    def get_exist_annotation_files(self):
        return self._annotations_files

    def set_all_img_files(self, files):
        self._img_files = files

    def set_annotation_files(self, files):
        self._annotations_files = files

    def get_image(self, index):
        return self._img_files[index]

    def get_annotation_file(self, index):
        return self._annotations_files[index]

    def _get_next_image_helper(self, index):
        while index < len(self._img_files) - 1:
            index += 1
            image_file = self._img_files[index]
            image_file_name = image_file.split(".")[0]
            if f"{image_file_name}" not in self._annotations_files:
                return index
        return None

    def get_next_annotation_image(self, index):
        image_index = self._get_next_image_helper(index)
        if image_index:
            return image_index
        if not image_index and len(self._img_files) != len(self._annotations_files):
            return self._get_next_image_helper(0)
