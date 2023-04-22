import os

import numpy as np
from PIL import Image

from src.models.data_labels import DataLabels

"""
.. module:: streamlit_img_label
   :synopsis: manage.
.. module author:: Changsin Lee
"""


class DartImageManager:
    """ImageManager
    Manage the image object.

    Args:
        image_folder(str): the image folder.
        image_labels(DataLabels.Image): parsed image labels object
    """

    def __init__(self, image_folder, image_labels: DataLabels.Image):
        """initiate module"""
        self.image_labels = image_labels
        self._img = Image.open(os.path.join(image_folder, image_labels.name))
        self._shapes = []
        self._current_shapes = []
        self._load_shapes()
        self._resized_ratio_w = 1
        self._resized_ratio_h = 1

    def get_img(self):
        """get the image object

        Returns:
            img(PIL.Image): the image object.
        """
        return self._img

    def _load_shapes(self):
        converted_shapes = []
        for label_object in self.image_labels.objects:
            shape = dict()
            if label_object.type == 'box':
                left, top, right, bottom = label_object.points
                width = right - left
                height = bottom - top
                shape['left'] = int(left)
                shape['top'] = int(top)
                shape['width'] = int(width)
                shape['height'] = int(height)
                shape['label'] = label_object.label
                shape['shapeType'] = 'box'
            elif label_object.type == 'spline' or label_object.type == 'boundary':
                points = []
                for point in label_object.points:
                    x, y, r = point
                    point_dict = dict()
                    point_dict['x'] = x
                    point_dict['y'] = y
                    point_dict['r'] = r
                    points.append(point_dict)

                shape['points'] = points
                shape['label'] = label_object.label
                shape['shapeType'] = label_object.type
            elif label_object.type == 'polygon' or label_object.type == 'VP':
                points = []
                for point in label_object.points:
                    x, y = point
                    point_dict = dict()
                    point_dict['x'] = x
                    point_dict['y'] = y
                    points.append(point_dict)

                shape['points'] = points
                shape['label'] = label_object.label
                shape['shapeType'] = label_object.type

            converted_shapes.append(shape)

        self._shapes = converted_shapes

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

    def _resize_shape(self, idx, shape):
        if not shape:
            return shape

        resized_shape = dict()
        resized_shape['shape_id'] = idx
        if shape['shapeType'] == 'box':
            resized_shape['left'] = shape['left'] / self._resized_ratio_w
            resized_shape['width'] = shape['width'] / self._resized_ratio_w
            resized_shape['top'] = shape['top'] / self._resized_ratio_h
            resized_shape['height'] = shape['height'] / self._resized_ratio_h
        elif shape['shapeType'] == 'spline' or shape['shapeType'] == 'boundary':
            resized_points = []
            for point in shape['points']:
                resized_point = dict()
                resized_point['x'] = int(point['x'] / self._resized_ratio_w)
                resized_point['y'] = int(point['y'] / self._resized_ratio_h)
                resized_point['r'] = int(point['r'] / self._resized_ratio_w)

                resized_points.append(resized_point)

            resized_shape['points'] = resized_points

        elif shape['shapeType'] == 'polygon' or shape['shapeType'] == 'VP':
            resized_points = []
            for point in shape['points']:
                resized_point = dict()
                resized_point['x'] = int(point['x'] / self._resized_ratio_w)
                resized_point['y'] = int(point['y'] / self._resized_ratio_h)

                resized_points.append(resized_point)

            resized_shape['points'] = resized_points

        if 'label' in shape:
            resized_shape['label'] = shape['label']
        resized_shape['shapeType'] = shape['shapeType']
        return resized_shape

    def get_resized_shapes(self):
        """get resized the rects according to the resized image.

        Returns:
            resized_rects(list): the resized bounding boxes of the image.
        """
        resized_shapes = []
        for idx, shape in enumerate(self._shapes):
            resized_shapes.append(self._resize_shape(idx, shape))

        return resized_shapes

    def _chop_shape_img(self, shape):
        raw_image = np.asarray(self._img).astype("uint8")
        width, height, alpha = raw_image.shape
        width = width if width > 0 else 1
        height = height if height > 0 else 1
        prev_img = np.zeros((width, height, alpha), dtype="uint8")

        label = ""
        if shape:
            if shape['shapeType'] == 'box':
                shape['left'] = int(shape['left'] * self._resized_ratio_w)
                shape['width'] = int(shape['width'] * self._resized_ratio_w)
                shape['top'] = int(shape['top'] * self._resized_ratio_h)
                shape['height'] = int(shape['height'] * self._resized_ratio_h)
                left, top, width, height = (
                    shape['left'],
                    shape['top'],
                    shape['width'],
                    shape['height']
                )
                top = top if top > 0 else 0
                left = left if left > 0 else 0
                width = width if width > 0 else 1
                height = height if height > 0 else 1
                prev_img[top: top + height, left: left + width] = raw_image[top: top + height, left: left + width]
                prev_img = prev_img[top: top + height, left: left + width]
            elif shape['shapeType'] == 'spline' or shape['shapeType'] == 'boundary':
                resized_points = []
                for point in shape['points']:
                    resized_point = dict()
                    resized_point['x'] = int(point['x'] / self._resized_ratio_w)
                    resized_point['y'] = int(point['y'] / self._resized_ratio_h)
                    resized_point['r'] = int(point['r'] / self._resized_ratio_w)

                    resized_points.append(resized_point)

            elif shape['shapeType'] == 'polygon' or shape['shapeType'] == 'VP':
                resized_points = []
                for point in shape['points']:
                    resized_point = dict()
                    resized_point['x'] = int(point['x'] / self._resized_ratio_w)
                    resized_point['y'] = int(point['y'] / self._resized_ratio_h)

                    resized_points.append(resized_point)

            if "label" in shape:
                label = shape["label"]
        return Image.fromarray(prev_img), label

    def init_annotation(self, shapes):
        """init annotation for current shapes.

        Args:
            shapes(list): the bounding boxes of the image.
        Returns:
            prev_img(list): list of preview images with default label.
        """
        self._current_shapes = shapes
        # return [self._chop_shape_img(shape) for shape in self._current_shapes]
        return [self._chop_shape_img(shapes)]

    def set_annotation(self, index, label):
        """set the label of the image.

        Args:
            index(int): the index of the list of bounding boxes of the image.
            label(str): the label of the bounding box
        """
        if label and label != 'No error':
            print("index {} label {}".format(index, label))

            if not self.image_labels.objects[index].verification_result:
                self.image_labels.objects[index].verification_result = dict()

            self.image_labels.objects[index].verification_result['error_code'] = label
