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
        self._selected_shape = dict()
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
                print(label_object.points)
                left, top, right, bottom = label_object.points[0]
                width = right - left
                height = bottom - top
                point_dict = dict()
                point_dict['x'] = left
                point_dict['y'] = top
                point_dict['w'] = width
                point_dict['h'] = height
                shape['points'] = [point_dict]
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
            point_dict = shape['points'][0]
            resized_point = dict()
            resized_point['x'] = point_dict['x'] / self._resized_ratio_w
            resized_point['w'] = point_dict['w'] / self._resized_ratio_w
            resized_point['y'] = point_dict['y'] / self._resized_ratio_h
            resized_point['h'] = point_dict['h'] / self._resized_ratio_h
            resized_shape['points'] = [resized_point]
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
                point_dict = shape['points'][0]
                resized_points = dict()
                resized_points['x'] = int(point_dict['x'] * self._resized_ratio_w)
                resized_points['w'] = int(point_dict['w'] * self._resized_ratio_w)
                resized_points['y'] = int(point_dict['y'] * self._resized_ratio_h)
                resized_points['h'] = int(point_dict['h'] * self._resized_ratio_h)

                x, y, w, h = (
                    resized_points['x'],
                    resized_points['y'],
                    resized_points['w'],
                    resized_points['h']
                )
                x = x if x > 0 else 0
                y = y if y > 0 else 0
                w = w if w > 0 else 1
                h = h if h > 0 else 1
                prev_img[y: y + h, x: x + w] = raw_image[y: y + h, x: x + w]
                prev_img = prev_img[y: y + h, x: x + w]
            elif shape['shapeType'] == 'spline' or shape['shapeType'] == 'boundary':
                resized_points = []
                for point in shape['points']:
                    resized_point_dict = dict()
                    resized_point_dict['x'] = point['x'] * self._resized_ratio_w
                    resized_point_dict['y'] = point['y'] * self._resized_ratio_h
                    resized_point_dict['r'] = point['r'] * self._resized_ratio_w

                    resized_points.append(resized_points)

            elif shape['shapeType'] == 'polygon' or shape['shapeType'] == 'VP':
                resized_points = []
                for point in shape['points']:
                    resized_point_dict = dict()
                    resized_point_dict['x'] = point['x'] * self._resized_ratio_w
                    resized_point_dict['y'] = point['y'] * self._resized_ratio_h

                    resized_points.append(resized_points)

            if "label" in shape:
                label = shape["label"]

        return Image.fromarray(prev_img), label

    def init_annotation(self, shape: dict):
        """init annotation for current shapes.

        Args:
            shape(dict): the bounding boxes of the image.
        Returns:
            prev_img(list): list of preview images with default label.
        """
        self._selected_shape = shape
        # return [self._chop_shape_img(shape) for shape in self._current_shapes]
        return self._chop_shape_img(shape)

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
