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
    def _get_class_attribute_name(meta_data_dict: dict):
        search_str = "task/labels/label/attributes/attribute/name"
        return utils.get_dict_value(meta_data_dict, search_str)
    # def _get_class_attribute_name(meta_data_dict: dict):
    #     search_str = "task/labels/label/attributes/attribute/name"
    #     return utils.get_dict_value(meta_data_dict, search_str)

    def _parse_class_names(self, meta_data_dict: dict):
        search_str = "task/labels/label"
        labels = utils.get_dict_value(meta_data_dict, search_str)

        classes = []
        for idx, label_dict in enumerate(labels):
            clazz = label_dict.get("name")
            category_dict = dict()
            category_dict['id'] = idx
            category_dict['name'] = clazz
            # category_dict['supercategory'] = ""

            classes.append(category_dict)
            self.categories[clazz] = idx

        return classes

    # def _parse_class_names(self, meta_data_dict: dict):
    #     search_str = "task/labels/label/attributes/attribute/values"
    #     values = utils.get_dict_value(meta_data_dict, search_str)
    #     if values:
    #         class_tokens = str(values).split('\n')
    #
    #         if class_tokens is None:
    #             return None
    #
    #         classes = []
    #         for idx, clazz in enumerate(class_tokens):
    #             category_dict = dict()
    #             category_dict['id'] = idx
    #             category_dict['name'] = clazz
    #             # category_dict['supercategory'] = ""
    #
    #             classes.append(category_dict)
    #             self.categories[clazz] = idx
    #
    #         return classes

    def write(self, file_in: str, file_out: str) -> None:
        def _create_converted_json():
            """
            create the template for the converted json
            """
            converted_json = dict()

            licenses = []
            default_license = dict()
            default_license["name"] = "MIT"
            default_license["id"] = 0
            default_license["url"] = ""

            licenses.append(default_license)

            converted_json["licenses"] = licenses

            info_dict = dict()
            info_dict["description"] = utils.get_dict_value(data_labels.meta_data, "task/project")
            info_dict["date_created"] = utils.get_dict_value(data_labels.meta_data, "task/created")

            converted_json["info"] = info_dict

            if data_labels.meta_data:
                converted_json["categories"] = self._parse_class_names(data_labels.meta_data)

            return converted_json

        data_labels = DataLabels.load(file_in)

        project_folder = os.path.dirname(file_in)
        cuboid_folder = os.path.join(project_folder, "cuboid")
        cuboid_filenames = utils.glob_files(cuboid_folder, SUPPORTED_LABEL_FILE_EXTENSIONS)
        cuboid_filenames.sort()

        for idx, image in enumerate(data_labels.images):
            converted_json = _create_converted_json()

            # 1. images
            converted_images = []
            converted_image = dict()
            converted_image["id"] = int(image.image_id)
            converted_image["width"] = image.width
            converted_image["height"] = image.height
            converted_image["file_name"] = image.name

            converted_images.append(converted_image)

            # 2. annotations
            converted_annotations = []
            annotation_id = 0
            if image.objects:
                for anno_object in image.objects:
                    annotation = dict()
                    annotation["id"] = int(anno_object.attributes["ID"])
                    annotation["image_id"] = int(image.image_id)
                    class_name = anno_object.label
                    annotation["category_id"] = self.categories[class_name]
                    annotation_id += 1

                    annotation["bbox"] = anno_object.points[0]

                    is_social_interaction = anno_object.attributes.get("Interaction")
                    if is_social_interaction:
                        attributes_dict = dict()
                        attributes_dict["is_social_interaction"] = False if is_social_interaction == "off" else True
                        annotation["attributes"] = attributes_dict

                    converted_annotations.append(annotation)

            converted_json["images"] = converted_images
            converted_json["annotations"] = converted_annotations

            # 3. pc_images
            # logger.info(f"## idx is {idx}/{len(cuboid_filenames)}")
            image_filename_stem = Path(image.name).stem
            filename_tokens = image_filename_stem.split('_')
            pcd_filename = Path(image.name).stem + ".pcd"

            pc_images = []

            pc_image_dict = dict()
            pc_image_dict["id"] = int(image.image_id)
            pc_image_dict["file_name"] = pcd_filename
            pc_image_dict["license"] = 0
            pc_image_dict["date_capture"] = utils.get_dict_value(data_labels.meta_data, "task/created")
            pc_images.append(pc_image_dict)

            converted_json["pc_images"] = pc_images

            # 4. pc_annotations
            cuboid_anno_filename = os.path.join(cuboid_folder, "00" + filename_tokens[-1] + ".json")
            if cuboid_anno_filename in cuboid_filenames:
                cuboid_labels = utils.from_file(cuboid_anno_filename)
                converted_json["pc_annotations"] = cuboid_labels
            else:
                converted_json["pc_annotations"] = []

            # 5. write out the converted json to a file
            json_data = json.dumps(converted_json, default=utils.default, ensure_ascii=False, indent=2)

            output_filename = os.path.join(os.path.dirname(file_out),
                                           image_filename_stem + ".json")
            utils.to_file(json_data, output_filename)


