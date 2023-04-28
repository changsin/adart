import copy
import os

import numpy as np
from PIL import Image

from src.models.data_labels import DataLabels

"""
.. module:: streamlit_img_label
   :synopsis: manage.
.. module author:: Changsin Lee
"""


class ImageManager:
    """ImageManager
    Manages the image object.

    Args:
        image_folder(str): the image folder.
        image_labels(DataLabels.Image): parsed image labels object
    """

    def __init__(self, image_folder, image_labels: DataLabels.Image):
        """initiate module"""
        self.image_labels = image_labels
        self._img = Image.open(os.path.join(image_folder, image_labels.name))
        # NB: note that the shapes should be all in the ShapeProps format defined in interfaces.tsx in the frontend
        self._shapes = []
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
        """
        loads shapes from DataLabels - note that the format of Objects (labels) changes as well.
        Notably, points -> [[pts],[pts]...] to [[x: ..][y: ..]...] and type -> shapeType
        :return:
        """
        converted_shapes = []
        for label_object in self.image_labels.objects:
            shape = dict()
            shape['label'] = label_object.label
            shape['attributes'] = label_object.attributes
            shape['verification_result'] = label_object.verification_result

            if label_object.type == 'box':
                left, top, right, bottom = label_object.points[0]
                width = right - left
                height = bottom - top
                point_dict = dict()
                point_dict['x'] = left
                point_dict['y'] = top
                point_dict['w'] = width
                point_dict['h'] = height
                shape['points'] = [point_dict]
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
                shape['shapeType'] = label_object.type

            converted_shapes.append(shape)

        self._shapes = converted_shapes

    @staticmethod
    def to_data_labels_shape(shape):
        """
        convert ShapeProps to DataLabels format
        :param shape: shape in the ShapeProps format
        :return: converted shape in the DataLabels format
        """
        converted_shape = copy.deepcopy(shape)
        converted_points = []
        if shape['shapeType'] == 'box':
            points = shape['points'][0]
            xtl, ytl = points['x'], points['y']
            xbr, ybr = xtl + points['w'], ytl + points['h']
            converted_points.append((xtl, ytl, xbr, ybr))
        elif shape['shapeType'] == 'spline' or shape['shapeType'] == 'boundary':
            for point in shape['points']:
                x, y, r = point['x'], point['y'], point['r']
                converted_points.append((x, y, r))
        elif shape['shapeType'] == 'polygon' or shape['shapeType'] == 'VP':
            for point in shape['points']:
                x, y = point['x'], point['y']
                converted_points.append((x, y))

        converted_shape['points'] = converted_points
        converted_shape['type'] = shape['shapeType']
        del converted_shape['shapeType']
        return converted_shape

    @staticmethod
    def get_bounding_rectangle(shape) -> list:
        resized_points = shape['points']
        min_x = max_x = int(resized_points[0]['x'])
        min_y = max_y = int(resized_points[0]['y'])

        # Iterate over the remaining control points and update the minimum and maximum x and y values
        for pt in resized_points[1:]:
            if pt['x'] < min_x:
                min_x = int(pt['x'])
            elif pt['x'] > max_x:
                max_x = int(pt['x'])
            if pt['y'] < min_y:
                min_y = int(pt['y'])
            elif pt['y'] > max_y:
                max_y = int(pt['y'])

        return [min_x, min_y, max_x, max_y]

    def resizing_img(self, min_width=700, min_height=700, max_height=1000, max_width=1000):
        """resizing the image by max_height and max_width.

        Args:
            min_width(int): the min_width of the frame.
            min_height(int): the min_height of the frame.
            max_width(int): the max_width of the frame.
            max_height(int): the max_height of the frame.
        Returns:
            resized_img(PIL.Image): the resized image.
        """
        resized_img = self._img.copy()
        if resized_img.height > max_height or resized_img.width > max_width:
            ratio = min(max_height / resized_img.height, max_width / resized_img.width)
            resized_img = resized_img.resize(
                (int(resized_img.width * ratio), int(resized_img.height * ratio))
            )
        if resized_img.height < min_height or resized_img.width < min_width:
            ratio = max(min_height / resized_img.height, min_width / resized_img.width)
            resized_img = resized_img.resize(
                (int(resized_img.width * ratio), int(resized_img.height * ratio))
            )

        self._resized_ratio_w = self._img.width / resized_img.width
        self._resized_ratio_h = self._img.height / resized_img.height

        return resized_img

    def upscale_shape(self, shape):
        scaled_shape = copy.deepcopy(shape)
        if scaled_shape['shapeType'] == 'box':
            points = scaled_shape['points'][0]
            points['x'] = points['x'] * self._resized_ratio_w
            points['y'] = points['y'] * self._resized_ratio_h
            points['w'] = points['w'] * self._resized_ratio_w
            points['h'] = points['h'] * self._resized_ratio_h
            scaled_shape['points'] = [points]
        elif shape['shapeType'] == 'spline' or shape['shapeType'] == 'boundary':
            scaled_points = []
            for point in shape['points']:
                scaled_point = dict()
                scaled_point['x'] = int(point['x'] * self._resized_ratio_w)
                scaled_point['y'] = int(point['y'] * self._resized_ratio_h)
                scaled_point['r'] = int(point['r'] * self._resized_ratio_w)
                scaled_points.append(scaled_point)

            scaled_shape['points'] = scaled_points

        elif shape['shapeType'] == 'polygon' or shape['shapeType'] == 'VP':
            scaled_points = []
            for point in shape['points']:
                scaled_point = dict()
                scaled_point['x'] = int(point['x'] * self._resized_ratio_w)
                scaled_point['y'] = int(point['y'] * self._resized_ratio_h)

                scaled_points.append(scaled_point)

            scaled_shape['points'] = scaled_points
        # TODO: later upscale other shape types as needed
        return scaled_shape

    def _downscale_shape(self, idx, shape):
        if not shape:
            return shape

        resized_shape = dict()
        resized_shape['shape_id'] = idx
        resized_shape['attributes'] = shape['attributes'] if shape['attributes'] else {}
        resized_shape['verification_result'] = shape['verification_result'] if shape['verification_result'] else {}
        resized_shape['shapeType'] = shape['shapeType']

        if 'label' in shape:
            resized_shape['label'] = shape['label']

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

        return resized_shape

    def get_resized_shapes(self):
        """get the resized shape according to the resized image.

        Returns:
            resized_shapes(list): the resized shapes.
        """
        resized_shapes = []
        for idx, shape in enumerate(self._shapes):
            resized_shapes.append(self._downscale_shape(idx, shape))

        return resized_shapes

    def get_preview_thumbnail(self, shape: dict) -> Image:
        """init annotation for current shapes.

        Args:
            shape(dict): the bounding boxes of the image.
        Returns:
            prev_img(list): list of preview images with default label.
        """
        raw_image = np.asarray(self._img).astype("uint8")
        width, height, alpha = raw_image.shape
        width = width if width > 0 else 1
        height = height if height > 0 else 1
        prev_img = np.zeros((width, height, alpha), dtype="uint8")

        label = ""
        if shape:
            if shape['shapeType'] == 'box':
                point_dict = shape['points'][0]
                x, y, w, h = (
                    int(point_dict['x']),
                    int(point_dict['y']),
                    int(point_dict['w']),
                    int(point_dict['h'])
                )
                x = x if x > 0 else 0
                y = y if y > 0 else 0
                w = w if w > 0 else 1
                h = h if h > 0 else 1

                x_end = x + w if x + w <= height else height
                y_end = y + h if y + h <= width else width

                prev_img[y:y_end, x:x_end] = raw_image[y:y_end, x:x_end]
                prev_img = prev_img[y:y_end, x:x_end]
            elif shape['shapeType'] == 'spline' or shape['shapeType'] == 'boundary' or shape['shapeType'] == 'polygon':
                min_x, min_y, max_x, max_y = ImageManager.get_bounding_rectangle(shape)
                min_x = min_x if min_x >= 0 else 0
                min_y = min_y if min_y >= 0 else 0
                max_x = max_x if max_x < self._img.width else self._img.width
                max_y = max_y if max_y < self._img.height else self._img.height
                print("{}:{}, {}:{}".format(min_y, max_y, min_x, max_x))

                prev_img[min_y:max_y, min_x:max_x] = raw_image[min_y:max_y, min_x:max_x]
                prev_img = prev_img[min_y:max_y, min_x:max_x]

            elif shape['shapeType'] == 'VP':
                resized_points = []
                for point in shape['points']:
                    resized_point_dict = dict()
                    resized_point_dict['x'] = point['x'] * self._resized_ratio_w
                    resized_point_dict['y'] = point['y'] * self._resized_ratio_h

                    resized_points.append(resized_points)

        return Image.fromarray(prev_img)

    def set_review(self, index, label, comment):
        """set the review label and comment.

        Args:
            index(int): the index of the list of bounding boxes of the image.
            label(str): the label of the bounding box
            comment(str): comment
        """
        if label and label != 'No error':
            verification_result = dict()
            if self.image_labels.objects[index].verification_result:
                verification_result = self.image_labels.objects[index].verification_result

            verification_result['error_code'] = label
            verification_result['comment'] = comment

            self.image_labels.objects[index].verification_result = verification_result
