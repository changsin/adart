from .base_reader import BaseReader
from src.common.utils import from_file

from src.common.logger import get_logger

logger = get_logger(__name__)


class HumanFReader(BaseReader):
    def parse(self, label_files, data_files=None):
        super().parse(label_files, data_files)

        images = list()
        for label_file in label_files:
            labels_dict = from_file(label_file)

            resolution = None

            images_list = None
            if labels_dict.get("Space_Info"):
                space_info_dict = labels_dict.get("Space_Info")
                images_list = space_info_dict["image_info"]

                if not isinstance(space_info_dict, list) and space_info_dict.get("Resolution"):
                    resolution = space_info_dict["Resolution"]
            else:
                images_list = labels_dict.get("Images")

            for image_id, image in enumerate(images_list):
                if not resolution:
                    resolution = image.get("Resolution")
                token1, token2 = resolution.split(",")
                width = int(token1)
                height = int(token2)

                image_dict = dict()
                image_dict["image_id"] = str(image_id)
                image_dict["name"] = image["ImageFileName"]
                image_dict["width"] = width
                image_dict["height"] = height

                annotations = image["seg_info"] if image.get("seg_info") else image.get("Seg_info")
                objects_list = list()

                for annotation_dict in annotations:
                    object_dict = dict()

                    attributes = list()
                    color_attrib = annotation_dict.get("color")
                    attributes_dict = dict()
                    attributes_dict["attribute_name"] = "color"
                    attributes_dict["attribute_value"] = color_attrib
                    attributes.append(attributes_dict)
                    object_dict["attributes"] = attributes

                    object_dict["label"] = annotation_dict.get("label")
                    object_dict["type"] = "segmentation"
                    object_dict["points"] = annotation_dict.get("points")
                    objects_list.append(object_dict)

                image_dict["objects"] = objects_list
                images.append(image_dict)

            self.data_labels_dict["images"] = images
        return self.data_labels_dict
