import json
import os.path
from pathlib import Path

import src.common.utils as utils
from src.common.logger import get_logger
from src.models.data_labels import DataLabels
from .base_writer import BaseWriter
from src.common.constants import SUPPORTED_LABEL_FILE_EXTENSIONS

logger = get_logger(__name__)


class Project85Writer(BaseWriter):
    def __init__(self):
        super().__init__()
        self.categories = dict()

    @staticmethod
    def _get_value(meta_data_dict: dict, search_str: str):
        cur_dict = meta_data_dict
        level_name_tokens = search_str.split('/')
        for token in level_name_tokens:
            cur_dict = cur_dict.get(token)

        return cur_dict

    @staticmethod
    def _get_class_attribute_name(meta_data_dict: dict):
        search_str = "task/labels/label/attributes/attribute/name"
        return Project85Writer._get_value(meta_data_dict, search_str)

    def _parse_class_names(self, meta_data_dict: dict):
        search_str = "task/labels/label/attributes/attribute/values"
        values = Project85Writer._get_value(meta_data_dict, search_str)
        if values:
            class_tokens = str(values).split('\n')

            if class_tokens is None:
                return None

            classes = []
            for idx, clazz in enumerate(class_tokens):
                category_dict = dict()
                category_dict['id'] = idx
                category_dict['name'] = clazz
                # category_dict['supercategory'] = ""

                classes.append(category_dict)
                self.categories[clazz] = idx

            return classes

    def write(self, file_in: str, file_out: str) -> None:
        data_labels = DataLabels.load(file_in)

        project_folder = os.path.dirname(file_in)
        cuboid_folder = os.path.join(project_folder, "cuboid")
        cuboid_filenames = utils.glob_files(cuboid_folder, SUPPORTED_LABEL_FILE_EXTENSIONS)
        cuboid_filenames.sort()
        logger.info("#################")
        logger.info(cuboid_filenames)

        converted_json = dict()

        licenses = []
        default_license = dict()
        default_license["name"] = "MIT"
        default_license["id"] = 0
        default_license["url"] = ""

        licenses.append(default_license)

        converted_json["licenses"] = licenses

        info_dict = dict()
        info_dict["date_created"] = Project85Writer._get_value(data_labels.meta_data, "task/created")
        info_dict["description"] = Project85Writer._get_value(data_labels.meta_data, "task/project")

        converted_json["info"] = info_dict

        if data_labels.meta_data:
            converted_json["categories"] = self._parse_class_names(data_labels.meta_data)

        # TODO: this does not seem to be right for the attribute name
        class_attribute_name = Project85Writer._get_class_attribute_name(data_labels.meta_data)

        for idx, image in enumerate(data_labels.images):
            converted_images = []
            converted_annotations = []
            annotation_id = 0

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
                    class_name = anno_object.attributes[class_attribute_name]
                    annotation["category_id"] = self.categories[class_name]
                    annotation_id += 1

                    annotation["bbox"] = anno_object.points[0]

                    converted_annotations.append(annotation)

            converted_json["images"] = converted_images
            converted_json["annotations"] = converted_annotations

            logger.info(f"## idx is {idx}")
            cuboid_filename = cuboid_filenames[idx]
            cuboid_labels = utils.from_file(cuboid_filename)

            # logger.info(cuboid_labels)
            # logger.info(converted_json)

            json_data = json.dumps(converted_json, default=utils.default, ensure_ascii=False, indent=2)

            image_filename_stem = Path(image.name).stem

            output_filename = os.path.join(os.path.dirname(file_out),
                                           image_filename_stem + ".json")
            utils.to_file(json_data, output_filename)


