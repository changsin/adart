import os
import xml.etree.ElementTree as ET

from .reader_base import ReaderBase


class StVisionReader(ReaderBase):
    @staticmethod
    def _parse_points(element: ET.Element) -> list:
        points = []
        for point in element.findall('Point'):
            x = point.get('x')
            y = point.get('y')
            if point.get('r'):
                r = point.get('r')
                points.append((float(x), float(y), float(r)))
            else:
                points.append((float(x), float(y)))
        return points

    @staticmethod
    def _parse_attributes(element: ET.Element) -> dict:
        attributes_dict = dict()
        # Iterate over the attributes of the element
        for attr_name, attr_value in element.attrib.items():
            # the attribute values are string in xml but converting them to numbers for ease of handling later on
            if element.tag.lower() == "occlusion":
                attributes_dict[attr_name] = float(attr_value)
            else:
                attributes_dict[attr_name] = int(attr_value)
        return attributes_dict

    @staticmethod
    def _parse_attributes_occlusions(element: ET.Element) -> dict:
        attributes_dict = StVisionReader._parse_attributes(element)

        # Specific to Spline & Boundary, it can have occlusion element
        # Add it as an attribute
        el_occlusions = element.findall('Occlusion')
        if el_occlusions:
            attributes_dict['occlusions'] = []
            for el_occlusion in el_occlusions:
                attributes_dict['occlusions'].append(StVisionReader._parse_attributes(el_occlusion))

        return attributes_dict

    def parse(self, label_files, data_files=None):
        super().parse(label_files, data_files)

        images = list()
        for image_id, xml_file in enumerate(label_files):
            xml_structure = ET.parse(xml_file)

            cur_img = dict()
            cur_img['image_id'] = str(image_id)
            cur_img['name'] = os.path.splitext(os.path.basename(xml_file))[0] + '.jpg'

            root = xml_structure.getroot()
            image_width = int(root.get('imageWidth'))
            image_height = int(root.get('imageHeight'))
            cur_img['width'] = image_width
            cur_img['height'] = image_height

            label_objects = []
            # Find the VP element
            el_vanishing_point = root.find('VP')
            if el_vanishing_point is not None and el_vanishing_point.get('hasVP'):
                vanishing_point_dict = dict()
                vanishing_point_dict['label'] = 'VP'
                vanishing_point_dict['type'] = 'VP'
                # Extract the VP coordinates
                x_ratio = float(el_vanishing_point.get('x_ratio'))
                y_ratio = float(el_vanishing_point.get('y_ratio'))
                # Convert to image coordinates and save it as a polygon point
                vanishing_point_dict['points'] = [[image_width * x_ratio, image_height * y_ratio]]

                # Add as an object (i.e., an annotation)
                label_objects.append(vanishing_point_dict)

            # Polygons, Boundarys, and Splines
            el_splines = root.find('Splines')
            if el_splines:
                for el_spline in el_splines.findall('Spline'):
                    spline_dict = dict()
                    spline_dict['label'] = el_spline.tag.lower()
                    spline_dict['type'] = el_spline.tag.lower()
                    # sort the control points by y as they can be out of order
                    spline_dict['points'] = sorted(StVisionReader._parse_points(el_spline),
                                                   key=lambda p: p[1])
                    spline_dict['attributes'] = StVisionReader._parse_attributes_occlusions(el_spline)
                    label_objects.append(spline_dict)

            el_polygons = root.find('Polygons')
            if el_polygons:
                for el_polygon in el_polygons.findall('Polygon'):
                    polygon_dict = dict()
                    polygon_dict['label'] = el_polygon.tag.lower()
                    polygon_dict['type'] = el_polygon.tag.lower()
                    polygon_dict['points'] = StVisionReader._parse_points(el_polygon)
                    polygon_dict['attributes'] = StVisionReader._parse_attributes(el_polygon)

                    label_objects.append(polygon_dict)

            el_boundaries = root.find('Boundarys')
            if el_boundaries:
                for el_boundary in el_boundaries.findall('Boundary'):
                    boundary_dict = dict()
                    boundary_dict['label'] = el_boundary.tag.lower()
                    boundary_dict['type'] = el_boundary.tag.lower()
                    boundary_dict['points'] = sorted(StVisionReader._parse_points(el_boundary),
                                                     key=lambda p: p[1])
                    boundary_dict['attributes'] = StVisionReader._parse_attributes_occlusions(el_boundary)
                    label_objects.append(boundary_dict)

            cur_img['objects'] = label_objects
            images.append(cur_img)

        self.data_labels_dict['images'] = images
        return self.data_labels_dict


