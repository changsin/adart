from .base_reader import BaseReader
from src.common.utils import from_file

from src.common.logger import get_logger

SHAPE_TYPES = ['KEYPOINTS', 'POLYGON']

logger = get_logger(__name__)


class LabelOnReader(BaseReader):
    @staticmethod
    def _parse_polygon_points(polygon_points: list) -> list:
        coordinates = []
        for i in range(0, len(polygon_points), 2):
            x = polygon_points[i]
            y = polygon_points[i + 1]
            coordinates.append((x, y))
        return coordinates

    @staticmethod
    def _parse_key_points(points: list) -> list:
        coordinates = []
        for i in range(0, len(points), 3):
            x = points[i]
            y = points[i + 1]
            z = points[i + 2]
            coordinates.append((x, y, z))
        return coordinates

    def parse(self, label_files, data_files=None):
        super().parse(label_files, data_files)

        images = list()
        for image_id, label_file in enumerate(label_files):
            labels_dict = from_file(label_file)

            width = int(labels_dict['IMAGE']['WIDTH'])
            height = int(labels_dict['IMAGE']['HEIGHT'])

            image_dict = dict()
            image_dict['image_id'] = str(image_id)
            image_dict['name'] = labels_dict['IMAGE']['IMAGE_FILE_NAME']
            image_dict['width'] = width
            image_dict['height'] = height

            annotations = labels_dict['ANNOTATION_INFO']
            objects_list = list()

            for annotation_dict in annotations:
                object_dict = dict()
                object_dict['label'] = annotation_dict.get("CATEGORY_NAME")
                if annotation_dict.get("POLYGON"):
                    object_dict['type'] = 'polygon'
                    object_dict['points'] = LabelOnReader._parse_polygon_points(annotation_dict.get("POLYGON"))
                elif annotation_dict.get("KEYPOINTS"):
                    object_dict['type'] = 'keypoint'
                    object_dict['points'] = LabelOnReader._parse_key_points(annotation_dict.get("KEYPOINTS"))

                objects_list.append(object_dict)

            image_dict['objects'] = objects_list
            images.append(image_dict)

            self.data_labels_dict['images'] = images
        return self.data_labels_dict
