from .base_writer import BaseWriter


import json
import src.common.utils as utils
from src.common.logger import get_logger
from src.models.data_labels import DataLabels

logger = get_logger(__name__)


class Project85Writer(BaseWriter):
    def __init__(self):
        super().__init__()
        self.categories = dict()

    def _parse_classes(self, meta_data_dict: dict):
        class_tokens = None

        attributes = meta_data_dict.get('task').get('labels').get('label').get('attributes')
        if attributes:
            logger.info(attributes)
            values = attributes.get('attribute').get('values')
            if values:
                class_tokens = values.split('\n')

        if class_tokens is None:
            return None

        classes = []
        for idx, clazz in enumerate(class_tokens):
            category_dict = dict()
            category_dict['id'] = idx
            category_dict['name'] = clazz
            category_dict['supercategory'] = ""

            classes.append(category_dict)
            self.categories[clazz] = idx

        return classes

    def write(self, file_in: str, file_out: str) -> None:
        data_labels = DataLabels.load(file_in)

        converted_json = dict()

        if data_labels.meta_data:
            converted_json["categories"] = self._parse_classes(data_labels.meta_data)

        converted_images = []
        converted_annotations = []
        annotation_id = 0
        for image in data_labels.images:
            converted_image = dict()
            converted_image["id"] = image.image_id
            converted_image["width"] = image.width
            converted_image["height"] = image.height
            converted_image["file_name"] = image.name

            converted_images.append(converted_image)

            if image.objects:
                for anno_object in image.objects:
                    annotation = dict()
                    annotation["id"] = annotation_id
                    annotation["image_id"] = image.image_id
                    # TODO: this does not seem to be right for the attribute name
                    class_name = anno_object.attributes['university']
                    annotation["category_id"] = self.categories[class_name]
                    annotation_id += 1

                    annotation["bbox"] = anno_object.points[0]

                    converted_annotations.append(annotation)

        converted_json["images"] = converted_images
        converted_json["annotations"] = converted_annotations

        logger.info(converted_json)
        json_data = json.dumps(converted_json, default=utils.default, ensure_ascii=False, indent=2)
        utils.to_file(json_data, file_out)


