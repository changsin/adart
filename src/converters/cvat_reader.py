from .reader_base import ReaderBase
import xml.etree.ElementTree as ET

BO_SHAPE_TYPES = ['box', 'polygon', 'polyline', 'points', 'face', 'body', 'leftHand', 'rightHand']


class CVATReader(ReaderBase):
    def parse(self, label_files, data_files=None):
        super().parse(label_files, data_files)

        label_file = label_files[0]

        xml_structure = ET.parse(label_file)

        root_info = xml_structure.getroot()

        if root_info.tag != 'annotations':
            raise Exception(label_file + 'is not a supported CVAT format.')

        image_info = root_info.findall('image')

        output_jdict_imgs = list()
        for each_img_info in image_info:
            cur_img = dict()
            cur_img['image_id'] = each_img_info.attrib['id']
            cur_img['name'] = each_img_info.attrib['name']
            cur_img['width'] = each_img_info.attrib['width']
            cur_img['height'] = each_img_info.attrib['height']

            cur_img_objlist = list()

            for objtype in BO_SHAPE_TYPES:
                obj_info = each_img_info.findall(objtype)

                for each_obj_info in obj_info:
                    cur_obj = dict()
                    cur_obj['label'] = each_obj_info.attrib['label']
                    cur_obj['type'] = objtype

                    try:
                        cur_obj['occluded'] = each_obj_info.attrib['occluded']
                    except KeyError:
                        cur_obj['occluded'] = "0"

                    try:
                        cur_obj['z_order'] = each_obj_info.attrib['z_order']
                    except KeyError:
                        cur_obj['z_order'] = "0"

                    try:
                        cur_obj['group_id'] = each_obj_info.attrib['group_id']
                    except KeyError:
                        cur_obj['group_id'] = ""

                    if objtype == 'box':
                        cur_obj['position'] = each_obj_info.attrib['xtl'] + ', ' + each_obj_info.attrib['ytl'] + ', ' + \
                                              each_obj_info.attrib['xbr'] + ', ' + each_obj_info.attrib['ybr']
                    else:
                        cur_obj['position'] = each_obj_info.attrib['points']

                    cur_obj_attrlist = list()
                    attr_infos = each_obj_info.findall('attribute')

                    for each_attr in attr_infos:
                        cur_attr = dict()
                        cur_attr['attribute_name'] = each_attr.attrib['name']
                        cur_attr['attribute_value'] = each_attr.text
                        cur_obj_attrlist.append(cur_attr)

                    cur_obj['attributes'] = cur_obj_attrlist

                    cur_img_objlist.append(cur_obj)

            cur_img['objects'] = cur_img_objlist
            output_jdict_imgs.append(cur_img)

        self.parsed_dict['images'] = output_jdict_imgs

        return self.parsed_dict
