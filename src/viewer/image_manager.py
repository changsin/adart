import copy

import numpy as np
from PIL import Image

from src.models.data_labels import DataLabels
from src.common.logger import get_logger

logger = get_logger(__name__)

"""
.. module:: streamlit_img_label
   :synopsis: manages the current image and shapes (labels)
   NB: the shapes are all in frontend coordinates (ShapeProps) and thus even the format is as such
    So here is the translation between DataLabels.Object and ShapeProps
                        DataLabels.Object                  ShapeProps
     shape type key:    type                               shapeType
     points format      points - list of list of           list of dictionaries,
                          floating point numbers             each of which has keyed values: x: 1 y: 2, etc
     point values       in image coordinates                screen coordinates,
                                                              specifically canvas coordinates
                                                              (700 or 1000 width)

    Inside ImageManager, it uses ShapeProps exclusively after the labels are loaded through DataLabels.
    The only exception is when the preview image is generated. In this case, the SHapeProps shape is
    converted into image coordinates.
    The other exception is, of course, when the shapes are saved into DataLabels.
    
    It is important to keep the format consistent. Inconsistent format standards will result in many woes.
         
.. module author:: Changsin Lee
"""


class ImageManager:
    """ImageManager
    Manages the image object - basically translating between DataLabel shapes and frontend shapes

    Args:
        image_filename(str): the image filename.
        data_label_image(DataLabels.Image): parsed image labels object
    """

    def __init__(self, image_filename: str, data_label_image: DataLabels.Image):
        """initiate module"""
        self._data_label_image = data_label_image
        self._image = Image.open(image_filename)
        # NB: note that the shapes should be all in the ShapeProps format defined in interfaces.tsx in the frontend
        self._shapes = []
        self._load_shapes()
        self._resized_ratio_w = 1
        self._resized_ratio_h = 1

    def get_image(self) -> Image:
        """get the image object

        Returns:
            image (PIL.Image): the image object.
        """
        return self._image

    def get_shape_by_id(self, shape_id: int) -> dict:
        for shape in self._shapes:
            if shape['shape_id'] == shape_id:
                return shape

    def add_shape(self, scaled_shape: dict):
        self._shapes.append(scaled_shape)

    def remove_shape(self, shape):
        shape_to_remove = self.get_shape_by_id(shape['shape_id'])
        if shape_to_remove:
            self._shapes.remove(shape_to_remove)

    def _load_shapes(self):
        """
        loads shapes from DataLabels - note that the format of Objects (labels) changes as well.
        Notably, points -> [[pts],[pts]...] to [[x: ..][y: ..]...] and type -> shapeType
        :return:
        """
        converted_shapes = []
        for shape_id, label_object in enumerate(self._data_label_image.objects):
            shape = dict()
            shape['shape_id'] = shape_id
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
    def to_data_labels_object(shape: dict) -> DataLabels.Object:
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

        return DataLabels.Object.from_json(converted_shape)

    def to_data_labels_image(self) -> DataLabels.Image:
        """
        convert ShapeProps to DataLabels format
        :param shape: shape in the ShapeProps format
        :return: converted shape in the DataLabels format
        """
        converted_objects = []
        for shape in self._shapes:
            converted_objects.append(ImageManager.to_data_labels_object(shape))

        self._data_label_image.objects = converted_objects
        return self._data_label_image

    @staticmethod
    def get_bounding_rectangle(shape) -> list:
        points = shape['points']
        x_values = [int(pt['x']) for pt in points]
        y_values = [int(pt['y']) for pt in points]

        if x_values and y_values:
            min_x = min(x_values)
            min_y = min(y_values)
            max_x = max(x_values)
            max_y = max(y_values)

            return [min_x, min_y, max_x, max_y]
        else:
            logger.warning(f"empty shape {shape}")

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
        resized_img = self._image.copy()
        if resized_img.width > max_width:
            ratio = min(max_height / resized_img.height, max_width / resized_img.width)
            resized_img = resized_img.resize(
                (int(resized_img.width * ratio), int(resized_img.height * ratio))
            )
        if resized_img.width < min_width:
            ratio = max(min_height / resized_img.height, min_width / resized_img.width)
            resized_img = resized_img.resize(
                (int(resized_img.width * ratio), int(resized_img.height * ratio))
            )

        self._resized_ratio_w = self._image.width / resized_img.width
        self._resized_ratio_h = self._image.height / resized_img.height

        return resized_img

    def upscale_shape(self, shape):
        scaled_shape = copy.deepcopy(shape)
        scaled_points = []
        if scaled_shape['shapeType'] == 'box':
            points = scaled_shape['points'][0]
            points['x'] = points['x'] * self._resized_ratio_w
            points['y'] = points['y'] * self._resized_ratio_h
            points['w'] = points['w'] * self._resized_ratio_w
            points['h'] = points['h'] * self._resized_ratio_h
            scaled_points.append(points)
        elif shape['shapeType'] == 'spline' or shape['shapeType'] == 'boundary':
            for point in shape['points']:
                scaled_point = dict()
                scaled_point['x'] = point['x'] * self._resized_ratio_w
                scaled_point['y'] = point['y'] * self._resized_ratio_h
                scaled_point['r'] = point['r'] * self._resized_ratio_w
                scaled_points.append(scaled_point)
        elif shape['shapeType'] == 'polygon' or shape['shapeType'] == 'VP':
            scaled_points = []
            for point in shape['points']:
                scaled_point = dict()
                scaled_point['x'] = int(point['x'] * self._resized_ratio_w)
                scaled_point['y'] = int(point['y'] * self._resized_ratio_h)
                scaled_points.append(scaled_point)

        scaled_shape['points'] = scaled_points
        # logger.info(f"shape: {shape} -> scaled_shape: {scaled_shape} ratio_w: {self._resized_ratio_w} ratio_h: {self._resized_ratio_h}")
        # TODO: later upscale other shape types as needed
        return scaled_shape

    def downscale_shape(self, shape):
        if not shape:
            return shape

        resized_shape = copy.deepcopy(shape)
        resized_points = []
        if shape['shapeType'] == 'box':
            point_dict = shape['points'][0]
            resized_point = dict()
            resized_point['x'] = point_dict['x'] / self._resized_ratio_w
            resized_point['w'] = point_dict['w'] / self._resized_ratio_w
            resized_point['y'] = point_dict['y'] / self._resized_ratio_h
            resized_point['h'] = point_dict['h'] / self._resized_ratio_h
            resized_points.append(resized_point)
        elif shape['shapeType'] == 'spline' or shape['shapeType'] == 'boundary':
            for point in shape['points']:
                resized_point = dict()
                resized_point['x'] = point['x'] / self._resized_ratio_w
                resized_point['y'] = point['y'] / self._resized_ratio_h
                resized_point['r'] = point['r'] / self._resized_ratio_w
                resized_points.append(resized_point)

                if shape.get('attributes') and shape.get('attributes').get('occlusions'):
                    del resized_shape['attributes']['occlusions']
                    occlusions = shape['attributes']['occlusions']

                    resized_occlusions = []
                    for occlusion in occlusions:
                        resized_occ = dict()
                        resized_occ['top'] = occlusion['top'] / self._resized_ratio_h
                        resized_occ['bottom'] = occlusion['bottom'] / self._resized_ratio_h
                        resized_occlusions.append(resized_occ)

                    resized_shape['attributes']['occlusions'] = resized_occlusions

        elif shape['shapeType'] == 'polygon' or shape['shapeType'] == 'VP':
            resized_points = []
            for point in shape['points']:
                resized_point = dict()
                resized_point['x'] = point['x'] / self._resized_ratio_w
                resized_point['y'] = point['y'] / self._resized_ratio_h
                resized_points.append(resized_point)

        resized_shape['points'] = resized_points
        return resized_shape

    def get_downscaled_shapes(self):
        """get the resized shape according to the resized image.

        Returns:
            resized_shapes(list): the resized shapes.
        """
        return [self.downscale_shape(shape) for shape in self._shapes]

    def get_preview_thumbnail(self, shape: dict) -> Image:
        """init annotation for current shapes.

        Args:
            shape(dict): the bounding boxes of the image.
        Returns:
            prev_img: PIL image of the preview thumbnail.
        """
        raw_image = np.asarray(self._image).astype("uint8")
        width, height, alpha = raw_image.shape
        width = max(width, 1)
        height = max(height, 1)
        prev_img = np.zeros((width, height, alpha), dtype="uint8")

        if shape:
            if shape['shapeType'] == 'box':
                point_dict = shape['points'][0]
                x, y, w, h = (
                    int(point_dict.get('x', 0)),
                    int(point_dict.get('y', 0)),
                    int(point_dict.get('w', 1)),
                    int(point_dict.get('h', 1))
                )
                x = max(x, 0)
                y = max(y, 0)
                w = max(w, 1)
                h = max(h, 1)

                x_end = min(x + w, height)
                y_end = min(y + h, width)

                prev_img[y:y_end, x:x_end] = raw_image[y:y_end, x:x_end]
                prev_img = prev_img[y:y_end, x:x_end]
            elif shape['shapeType'] == 'spline' or shape['shapeType'] == 'boundary' or shape['shapeType'] == 'polygon':
                bounding_rectangle = ImageManager.get_bounding_rectangle(shape)
                if bounding_rectangle:
                    min_x, min_y, max_x, max_y = bounding_rectangle
                    min_x = max(min_x, 0)
                    min_y = max(min_y, 0)
                    max_x = min(max_x, self._image.width)
                    max_y = min(max_y, self._image.height)

                    prev_img[min_y:max_y, min_x:max_x] = raw_image[min_y:max_y, min_x:max_x]
                    prev_img = prev_img[min_y:max_y, min_x:max_x]

            elif shape['shapeType'] == 'VP':
                resized_points = []
                for point in shape['points']:
                    resized_point_dict = {
                        'x': point.get('x', 0) * self._resized_ratio_w,
                        'y': point.get('y', 0) * self._resized_ratio_h
                    }
                    resized_points.append(resized_point_dict)

        return Image.fromarray(prev_img)

    def set_review(self, shape_id, error_code, comment):
        """set the review label and comment.

        Args:
            shape_id(int): shape id.
            error_code(str): the error code
            comment(str): comment
        """
        verification_result = None
        if error_code and error_code != 'No error':
            verification_result = dict()
            verification_result['error_code'] = error_code
            verification_result['comment'] = comment

        self._shapes[shape_id]['verification_result'] = verification_result
