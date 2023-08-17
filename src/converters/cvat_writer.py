import xml.etree.ElementTree as ET

from .base_writer import BaseWriter


CVAT_VERSION = 1.1


class CVATWriter(BaseWriter):
    def write(self, data_labels_dict: dict, filename: str) -> None:
        # Create the root element
        el_root = ET.Element("annotations")

        # Create child elements and add them to the root
        el_version = ET.SubElement(el_root, "version")
        el_version.text = CVAT_VERSION

        el_labels = ET.SubElement(el_root, "labels")



