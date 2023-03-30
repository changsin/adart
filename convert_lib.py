#-*- coding:utf-8 -*-
import json
import os
import shutil
import xml.etree.ElementTree as ET

import streamlit as st


# function name : collect_org_annofile_as_list
#
# 데이터 폴더(target_data_directory)에 있는, 확장자가 file_ext인 어노테이션 파일의 list를 반환하는 함수
# 반환되는 list의 크기는 이미지ㅡ어노테이션파일의 관계에 따라서 1개 or N개(이미지 개수)가 될 수 있음
#
# return value : org_annofile_list
def collect_org_annofile_as_list(target_data_directory, file_ext, image_annofile_relationship):
    org_annofile_list = list()
    # 폴더는 사용자(검수자를 관리하는 PM)가 데이터 폴더(target_data_directory)의 1-depth 구조로 컨트롤한다고 가정했기 때문에
    # os 라이브러리의 listdir를 통해서 데이터 탐색
    for eachf in os.listdir(target_data_directory):
        fname, ext = os.path.splitext(eachf)

        # os.path.splitext를 통해서 받아오는 파일 확장자는 '.{파일확장자}'이기 떄문에
        # 우측 인자에 '.'을 추가로 붙여줘야 기능 오류 없이 정상적으로 작업 진행
        if ext.lower() == '.' + file_ext:
            org_annofile_list.append(eachf)

            # 이미지 : 어노테이션 파일의 관계가 N : 1 (N!)인 경우
            # 이미지가 다수인 것 대비, 어노테이션 파일은 1개이기 때문에
            if image_annofile_relationship == 'N1':
                break


    return org_annofile_list

# Blackolive(CVAT) xml 파일을 검증도구에서 사용할 포맷으로 변경할 때 사용하는 함수
def convert_CVAT_to_Form(img_annof_relation, data_directory, annotation_fmt, destination_folder):
    # Blackolive가 지원하는 객체 타입
    BO_object_types = ['box', 'polygon', 'polyline', 'points', 'face', 'body', 'leftHand', 'rightHand']

    # file_format : 어노테이션 파일 포맷('xml')
    # anno_file_list : 현재 데이터 폴더(data_directory)에 있는 어노테이션 파일의 목록
    file_format = annotation_fmt.split(' ')[-1]
    anno_file_list = collect_org_annofile_as_list(data_directory, file_format, img_annof_relation)

    for id in range(len(anno_file_list)):

        output_jdict = dict()

        xml_structure = ET.parse(os.path.join(data_directory, anno_file_list[id]))

        # tag 이름은 find_all로 찾는다.
        # 대신, 중복된 태그가 있을 수 있으니 무조건 absolute path로 탐색
        # root의 경우, ElementTree의 getroot 함수를 통해서 노드를 받아옴.
        root_info = xml_structure.getroot()

        # pascal voc tag의 root tag는 'annotation'이기 때문에
        # 아닌 경우 Exception을 호출한다.
        # added at 22.04.01
        if root_info.tag != 'annotations':
            raise Exception(os.path.join(data_directory, anno_file_list[id]) + '는 Blackolive XML 포맷이 아닙니다.')

        # 1개만 있는 태그는 find 명령어 사용
        # N개 있는 태그는 findall 명령어를 통해서 탐색 수행
        image_info = root_info.findall('image')

        # 최종 산출물인 json 파일에 default로 들어있는 key-value값
        output_jdict['mode'] = 'annotation'
        output_jdict['twconverted'] = '96E7D8C8-44E4-4055-8487-85B3208E51A2'
        output_jdict['template_version'] = "0.1"

        # output_jdict_imgs : 최종 산출물인 json 파일의 images의 value가 될 이미지 list
        output_jdict_imgs = list()
        for each_img_info in image_info:
            cur_img = dict()
            cur_img['image_id'] = each_img_info.attrib['id']
            cur_img['name'] = each_img_info.attrib['name']
            cur_img['width'] = each_img_info.attrib['width']
            cur_img['height'] = each_img_info.attrib['height']

            # cur_img_objlist : 현재 이미지가 가지고 있는 객체('objects')의 value가 될 객체 list
            cur_img_objlist = list()

            # Blackolive가 지원하는 객체에 대한 태그를 모두 findall로 찾아서 탐색 필요하기 떄문에 선언한 for loop
            for objtype in BO_object_types:
                obj_info = each_img_info.findall(objtype)

                # 각 객체 type에 대한 for loop
                for each_obj_info in obj_info:
                    cur_obj = dict()
                    cur_obj['label'] = each_obj_info.attrib['label']
                    cur_obj['type'] = objtype

                    # occluded, z_order, group_id의 경우 필수 항목이 아니었던 거로 기억하기 때문에
                    # try ~ except 구문을 통해서 예외처리가 필요하다.
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


                    # 현재 품질 검증 도구에서는
                    # box의 경우 "xtl_value, ytl_value, xbr_value, ybr_value"로
                    # 그 외의 경우에는, 태그에 points라는 속성의 값(x1_value,y1_value;x2_value,y2_value;...;)이 있어서
                    # 해당 값을 집어넣어주면 된다.
                    if objtype == 'box':
                        cur_obj['position'] = each_obj_info.attrib['xtl'] + ', ' + each_obj_info.attrib['ytl'] + ', ' + each_obj_info.attrib['xbr'] + ', ' + each_obj_info.attrib['ybr']
                    else:
                        cur_obj['position'] = each_obj_info.attrib['points']


                    # 추가적으로 blackolive는 속성 태그(attribute)가 존재하기 때문에
                    # 이에 대한 loop 처리도 필요하다.
                    cur_obj_attrlist = list()
                    attr_infos = each_obj_info.findall('attribute')

                    for each_attr in attr_infos:
                        cur_attr = dict()
                        cur_attr['attribute_name'] = each_attr.attrib['name']
                        cur_attr['attribute_value'] = each_attr.text
                        cur_obj_attrlist.append(cur_attr)

                    cur_obj['attributes'] = cur_obj_attrlist

                    # 각 객체에 대한 처리가 완료되면, cur_img_objlist에 현재 객체(cur_obj)를 추가해준다.
                    cur_img_objlist.append(cur_obj)


            cur_img['objects'] = cur_img_objlist

            # 현재 이미지(cur_img)에 대한 처리가 완료되면, output_jdict_imgs에 현재 이미지 관련 정보를 추가한다.
            output_jdict_imgs.append(cur_img)

        output_jdict['images'] = output_jdict_imgs

        # 최종 산출물일 dictionary 객체(output_jdict) 연산이 완료되면
        # 우선 원본 어노테이션 파일을 데이터 폴더\origin 폴더로 이동시켜서 원본 어노테이션 파일(xml)을 백업한다.
        fname, ext = os.path.splitext(anno_file_list[id])
        shutil.copy(os.path.join(data_directory, anno_file_list[id]),
                    os.path.join(destination_folder, os.path.basename(anno_file_list[id])))

        # 그리고나서, 원본 어노테이션 파일이름.json으로 데이터를 저장하면 작업이 완료된다.
        with open(os.path.join(destination_folder, fname + '.json'), 'w', encoding='utf-8') as jf:
            json.dump(output_jdict, jf, indent=4, ensure_ascii=False)

        st.write("Converted {}".format(anno_file_list[id]))


# 우선은 default PASCAL VOC 포맷처럼, bounding box에 대한 변환작업만 수행
def convert_PASCAL_to_Form(img_annof_relation, data_directory, annotation_fmt):
    # file_format : 어노테이션 파일 포맷('xml')
    # anno_file_list : 현재 데이터 폴더(data_directory)에 있는 어노테이션 파일의 목록
    file_format = annotation_fmt.split(' ')[-1]
    anno_file_list = collect_org_annofile_as_list(data_directory, file_format, img_annof_relation)

    if img_annof_relation == '11':
        output_jdict = dict()

        # 최종 산출물인 json 파일에 default로 들어있는 key-value값
        output_jdict['mode'] = 'annotation'
        output_jdict['twconverted'] = '96E7D8C8-44E4-4055-8487-85B3208E51A2'
        output_jdict['template_version'] = "0.1"

        # output_jdict_imgs : 최종 산출물인 json 파일의 images의 value가 될 이미지 list
        output_jdict_imgs = list()

        # PASCAL VOC의 경우, 이미지 : 어노테이션 파일의 관계가 1 : 1이기 때문에
        # 별도의 image_id 정보가 없다.
        # id_idx가 대신 image_id 역할을 하기위해 선언한 변수
        id_idx = 0

        # PASCAL VOC의 경우, 이미지 : 어노테이션 파일의 관계가 1 : 1이기 때문에
        # 어노테이션 파일 개수만큼 for loop를 수행해야 output_jdict의 images value를 얻어낼 수 있다.
        for each_xmlfile in anno_file_list:
            xml_structure = ET.parse(os.path.join(data_directory, each_xmlfile))

            # tag 이름은 find_all로 찾는다.
            # 대신, 중복된 태그가 있을 수 있으니 무조건 absolute path로 탐색
            # root의 경우, ElementTree의 getroot 함수를 통해서 노드를 받아옴.
            root_info = xml_structure.getroot()


            # pascal voc tag의 root tag는 'annotation'이기 때문에
            # 아닌 경우 Exception을 호출한다.
            # added at 22.04.01
            if root_info.tag != 'annotation':
                raise Exception(os.path.join(data_directory, each_xmlfile) + '는 PASCAL VOC XML 포맷이 아닙니다.')


            # 1개만 있는 태그는 find 명령어 사용
            # N개 있는 태그는 findall 명령어를 통해서 탐색 수행
            cur_img = dict()
            cur_img['image_id'] = str(id_idx)
            id_idx += 1

            filename_tag = root_info.find('filename')
            cur_img['name'] = os.path.basename(filename_tag.text)

            # xml 파일의 text의 경우, 데이터 형변환(숫자라면 integer를 쫓아감)을 따라가는 경향이 있음.
            # 현재 만들어준 json의 value들은 속성의 값(attribute value)로부터 형 변환이 수행되어왔기 떄문에
            # string을 변환해주는 작업이 필요하다.
            img_resol_info = root_info.find('size')
            img_width_info = img_resol_info.find('width')
            img_height_info = img_resol_info.find('height')
            cur_img['width'] = str(img_width_info.text)
            cur_img['height'] = str(img_height_info.text)

            # cur_img_objlist : 현재 이미지가 가지고 있는 객체('objects')의 value가 될 객체 list
            cur_img_objlist = list()

            obj_info = root_info.findall('object')

            for each_obj_info in obj_info:
                cur_obj = dict()
                label_name_info = each_obj_info.find('name')
                cur_obj['label'] = label_name_info.text
                # PASCAL VOC는 기본적으로 box만 지원하기 때문에 type에 대해서 고민 X
                cur_obj['type'] = 'box'
                cur_obj['occluded'] = "0"
                cur_obj['z_order'] = "0"
                # PASCAL VOC는 기본적으로 객체들이 다 독립적이기 때문에 group_id의 value는 빈 문자열("")로 지정
                cur_obj['group_id'] = ""

                box_info = each_obj_info.find('bndbox')
                xtl_info = box_info.find('xmin')
                ytl_info = box_info.find('ymin')
                xbr_info = box_info.find('xmax')
                ybr_info = box_info.find('ymax')

                cur_obj['position'] = str(xtl_info.text) + ', ' + str(ytl_info.text) + ', ' + str(xbr_info.text) + ', ' + str(ybr_info.text)

                cur_obj_attrlist = list()
                cur_obj['attributes'] = cur_obj_attrlist

                # 각 객체에 대한 처리가 완료되면, cur_img_objlist에 현재 객체(cur_obj)를 추가해준다.
                cur_img_objlist.append(cur_obj)


            cur_img['objects'] = cur_img_objlist


            # 현재 이미지(cur_img)에 대한 처리가 완료되면, output_jdict_imgs에 현재 이미지 관련 정보를 추가한다.
            output_jdict_imgs.append(cur_img)


        output_jdict['images'] = output_jdict_imgs


        # 최종 산출물일 dictionary 객체(output_jdict) 연산이 완료되면
        # 우선 원본 어노테이션 파일을 데이터 폴더\origin 폴더로 이동시켜서 원본 어노테이션 파일들(xml)을 백업한다.
        for each_annofile in anno_file_list:
            shutil.move(os.path.join(data_directory, each_annofile), os.path.join(data_directory, 'origin'))

        fname, ext = os.path.splitext(anno_file_list[0])

        # 그리고나서, 첫 번째 원본 어노테이션 파일이름.json으로 데이터를 저장하면 작업이 완료된다.
        with open(os.path.join(data_directory, fname + '.json'), 'w', encoding='utf-8') as jf:
            json.dump(output_jdict, jf, indent=4, ensure_ascii=False)


# COCO json 파일을 검증도구에서 사용할 포맷으로 변경할 때 사용하는 함수
def convert_COCO_to_Form(img_annof_relation, data_directory, annotation_fmt):
    # file_format : 어노테이션 파일 포맷('xml')
    # anno_file_list : 현재 데이터 폴더(data_directory)에 있는 어노테이션 파일의 목록
    file_format = annotation_fmt.split(' ')[-1]
    anno_file_list = collect_org_annofile_as_list(data_directory, file_format, img_annof_relation)


    if img_annof_relation == 'N1':
        output_jdict = dict()

        with open(os.path.join(data_directory, anno_file_list[0]), 'r', encoding='utf-8') as jf:
            coco_jdict = json.load(jf)

        # COCO json의 경우, images, annotations, categories라는 key를 가지고 있으며
        # images : 현재 어노테이션 파일의 target인 이미지들의 list
        # annotations : 현재 어노테이션 파일이 표기한 객체들의 list
        # categories : 현재 어노테이션 파일의 class category의 list
        coco_img_list = coco_jdict['images']
        coco_label_list = coco_jdict['categories']
        coco_anno_list = coco_jdict['annotations']


        # 기본적으로 COCO json의 category는
        # 'id', 'name', 'supercategory'라는 3개의 key를 보관하고 있다.
        # 'name'(우리가 class라고 부르는 대상)의 상위 개체를 'supercategory'로 표기하지만
        # 현재 변환 기능에서는 필요하지 않은 정보이므로
        #
        # { "category_id" : "class 이름" }인 dictionary를 만들어주는 과정을 아래 line의 코드에서 수행한다.
        coco_label_dict = dict()
        for each_label in coco_label_list:
            coco_label_dict[each_label['id']] = each_label['name']


        # 기본적으로 COCO json의 image는
        # 우리가 필요한 "id", "file_name", "width", "height"의 key를 보관하고 있다.
        #
        # 아래 line의 코드에서는
        # {
        #     "image_id" : {
        #                      "dest_image_id" :,
        #                      "dest_name" :,
        #                      "dest_width" :,
        #                      "dest_height" :,
        #                      "dest_objects" : []
        #                   }
        # }
        # 인 dictionary를 만들어주는 과정을 수행한다.
        coco_image_dict = dict()
        for each_img in coco_img_list:
            cur_img = dict()
            cur_img['image_id'] = str(each_img['id'])
            cur_img['name'] = str(each_img['file_name'])
            cur_img['width'] = str(each_img['width'])
            cur_img['height'] = str(each_img['height'])
            cur_img['objects'] = list()

            coco_image_dict[each_img['id']] = cur_img


        # 기본적으로 COCO json의 annotations는
        # 해당 객체의 최외곽 사각형을 라벨링한 'box'라는 key와
        # 해당 객체를 구성하는 1개 이상의 polygon(1개 이상인 경우, 앞의 객체로 겹쳐진 경우 각각)을 라벨링한
        # 'segmentation'이라는 key를 보관하고 있다.
        #
        # 따라서, box 객체와, segmentation을 구성하는 각 polygon은 동일한 객체를 의미하기 때문에
        # 최종 산출물인 tw json annotation 파일에서는 group_id라는 key를 통해서 동일한 객체를 표기하도록 해야한다.
        # 아래 cur_group_id는 group_id의 value 역할을 수행하기 위한 변수이다.
        cur_group_id = 0
        for each_anno in coco_anno_list:
            # box 객체에 대한 정보를 추가해주는 코드
            cur_box_obj = dict()
            cur_box_obj['label'] = coco_label_dict[each_anno['category_id']]
            cur_box_obj['type'] = 'box'
            cur_box_obj['occluded'] = "0"
            cur_box_obj['z_order'] = "0"
            cur_box_obj['group_id'] = str(cur_group_id)

            box_position = str(each_anno['bbox'][0]) + ', ' + str(each_anno['bbox'][1]) + ', ' + str(each_anno['bbox'][0] + each_anno['bbox'][2]) + ', ' + str(each_anno['bbox'][1] + each_anno['bbox'][3])

            cur_box_obj['position'] = box_position

            # 대응하는 이미지에, box 객체(cur_box_obj) 정보를 추가해주는 코드
            coco_image_dict[each_anno['image_id']]['objects'].append(cur_box_obj)

            # polygons : segmentation을 구성하는 polygon 객체
            polygons = each_anno['segmentation']

            # 따라서 1회 이상 for loop 연산을 수행한다.
            for each_polygon in polygons:
                cur_obj = dict()
                cur_obj['label'] = coco_label_dict[each_anno['category_id']]
                cur_obj['type'] = 'polygon'
                cur_obj['occluded'] = "0"
                cur_obj['z_order'] = "0"
                cur_obj['group_id'] = str(cur_group_id)

                num_of_points = len(each_polygon) // 2

                str_point_list = list()

                for idx in range(num_of_points):
                    new_point = str(each_polygon[2*idx]) + ',' + str(each_polygon[2*idx+1])
                    str_point_list.append(new_point)

                cur_obj['position'] = ';'.join(str_point_list)

                # 대응하는 이미지에, polygon 객체(cur_obj) 정보를 추가해주는 코드
                coco_image_dict[each_anno['image_id']]['objects'].append(cur_obj)

            cur_group_id += 1


        new_img_list = list()
        for each_key in coco_image_dict:
            new_img_list.append(coco_image_dict[each_key])


        # 최종 산출물인 json 파일에 default로 들어있는 key-value값
        output_jdict['mode'] = 'annotation'
        output_jdict['twconverted'] = '96E7D8C8-44E4-4055-8487-85B3208E51A2'
        output_jdict['template_version'] = "0.1"
        
        output_jdict['images'] = new_img_list


        # 최종 산출물일 dictionary 객체(output_jdict) 연산이 완료되면
        # 우선 원본 어노테이션 파일을 데이터 폴더\origin 폴더로 이동시켜서 원본 어노테이션 파일(json)을 백업한다.
        # 아래 저장하는 코드와 순서가 바뀌면
        # 원본 어노테이션 정보가 날아가는 오류가 발생하기 때문에 주의가 필요하다.
        shutil.move(os.path.join(data_directory, anno_file_list[0]), os.path.join(data_directory, 'origin'))

        fname, ext = os.path.splitext(anno_file_list[0])

        # 그리고나서, 원본 어노테이션 파일이름.json으로 데이터를 저장하면 작업이 완료된다.
        with open(os.path.join(data_directory, fname + '.json'), 'w', encoding='utf-8') as jf:
            json.dump(output_jdict, jf, indent=4, ensure_ascii=False)


# SuperbAI의 json 파일을 검증도구에서 사용할 포맷으로 변경할 떄 사용하는 함수
def convert_SUPERBAI_to_Form(img_annof_relation, data_directory, annotation_fmt):
    # file_format : 어노테이션 파일 포맷('xml')
    # anno_file_list : 현재 데이터 폴더(data_directory)에 있는 어노테이션 파일의 목록
    file_format = annotation_fmt.split(' ')[-1]
    anno_file_list = collect_org_annofile_as_list(data_directory, file_format, img_annof_relation)

    if img_annof_relation == '11':
        output_jdict = dict()

        # SuperbAI가 지원하는 객체 타입
        SuperbAI_object_types = ['box', 'polygon', 'polyline']

        # 최종 산출물인 json 파일에 default로 들어있는 key-value값
        output_jdict['mode'] = 'annotation'
        output_jdict['twconverted'] = '96E7D8C8-44E4-4055-8487-85B3208E51A2'
        output_jdict['template_version'] = "0.1"

        # output_jdict_imgs : 최종 산출물인 json 파일의 images의 value가 될 이미지 list
        output_jdict_imgs = list()

        # 전달받은 Superb AI 데이터의 경우, 이미지 : 어노테이션 파일의 관계가 1 : 1이기 때문에
        # 별도의 image_id 정보가 없다.
        # id_idx가 대신 image_id 역할을 하기위해 선언한 변수
        id_idx = 0

        # 전달받은 Superb AI 데이터의 경우, 이미지 : 어노테이션 파일의 관계가 1 : 1이기 때문에
        # 어노테이션 파일 개수만큼 for loop를 수행해야 output_jdict의 images value를 얻어낼 수 있다.
        for each_jsonfile in anno_file_list:
            cur_img = dict()
            cur_img['image_id'] = str(id_idx)
            id_idx += 1

            with open(os.path.join(data_directory, each_jsonfile), 'r', encoding='utf-8') as jf:
                superb_jdict = json.load(jf)

            cur_img['name'] = os.path.basename(superb_jdict['data_key'])

            # 전달받은 Superb AI 데이터의 경우, 이미지의 width, height 정보가 없다.
            # 따라서, width 및 height 정보를 빈 문자열('')로 값을 지정해준다.
            cur_img['width'] = ''
            cur_img['height'] = ''

            # cur_img_objlist : 현재 이미지가 가지고 있는 객체('objects')의 value가 될 객체 list
            cur_img_objlist = list()

            # 전달받은 Superb AI 데이터의 경우, 라벨링 데이터가 이중으로 묶여있는 특이한 형태를 띄기 때문에 주의가 필요하다.
            obj_info = superb_jdict['annotation_result']['objects']


            for each_obj_info in obj_info:
                cur_obj = dict()

                # 전달받은 Superb AI 데이터의 경우, 객체 type(shape)가 단일 key-value로 이루어진 dictionry이기 떄문에
                # dictionary.items로 1번째 인덱스와 그외로 접근하는 방식을 택함
                shape_value = each_obj_info['shape']
                (shape_type, position_info), = shape_value.items()

                # 전달받은 Superb AI 데이터의 경우, COCO style의 keypoint를 지원하기 때문에
                # keypoint는 변환 작업을 수행하지 않도록 if 분기문 사용
                if shape_type not in SuperbAI_object_types:
                    continue

                cur_obj['type'] = shape_type
                cur_obj['label'] = each_obj_info['class']
                cur_obj['occluded'] = "0"
                cur_obj['z_order'] = "0"
                cur_obj['group_id'] = ""

                if shape_type == 'box':
                    xtl = position_info['x']
                    ytl = position_info['y']
                    xbr = position_info['x'] + position_info['width']
                    ybr = position_info['y'] + position_info['height']

                    position_value = str(xtl) + ', ' + str(ytl) + ', ' + str(xbr) + ', ' + str(ybr)

                # shape_type이 polygon이나 polyline인 경우
                else:
                    str_point_list = list()
                    for each_point in position_info:
                        str_point = str(each_point['x']) + ',' + str(each_point['y'])
                        str_point_list.append(str_point)

                    position_value = ';'.join(str_point_list)

                cur_obj['position'] = position_value


                cur_obj_attrlist = list()

                for each_attr in each_obj_info['properties']:
                    cur_attr = dict()
                    cur_attr['attribute_name'] = each_attr['name']
                    cur_attr['attribute_value'] = each_attr['value']
                    cur_obj_attrlist.append(cur_attr)

                cur_obj['attributes'] = cur_obj_attrlist

                # 각 객체에 대한 처리가 완료되면, cur_img_objlist에 현재 객체(cur_obj)를 추가해준다.
                cur_img_objlist.append(cur_obj)


            cur_img['objects'] = cur_img_objlist

            # 현재 이미지(cur_img)에 대한 처리가 완료되면, output_jdict_imgs에 현재 이미지 관련 정보를 추가한다.
            output_jdict_imgs.append(cur_img)

        output_jdict['images'] = output_jdict_imgs

        # 최종 산출물일 dictionary 객체(output_jdict) 연산이 완료되면
        # 우선 원본 어노테이션 파일을 데이터 폴더\origin 폴더로 이동시켜서 원본 어노테이션 파일들(json)을 백업한다.
        for each_annofile in anno_file_list:
            shutil.move(os.path.join(data_directory, each_annofile), os.path.join(data_directory, 'origin'))

        fname, ext = os.path.splitext(anno_file_list[0])

        # 그리고나서, 첫 번째 원본 어노테이션 파일이름.json으로 데이터를 저장하면 작업이 완료된다.
        with open(os.path.join(data_directory, fname + '.json'), 'w', encoding='utf-8') as jf:
            json.dump(output_jdict, jf, indent=4, ensure_ascii=False)


# AIMMO의 json 파일을 검증도구에서 사용할 포맷으로 변경할 떄 사용하는 함수
def convert_AIMMO_to_Form(img_annof_relation, data_directory, annotation_fmt):
    # file_format : 어노테이션 파일 포맷('xml')
    # anno_file_list : 현재 데이터 폴더(data_directory)에 있는 어노테이션 파일의 목록
    file_format = annotation_fmt.split(' ')[-1]
    anno_file_list = collect_org_annofile_as_list(data_directory, file_format, img_annof_relation)

    if img_annof_relation == '11':
        output_jdict = dict()

        # AIMMO가 지원하는 객체 타입
        Annotation_AI_object_types = { 'bbox' : 'box', 'poly_seg' : 'polygon' }


        # 최종 산출물인 json 파일에 default로 들어있는 key-value값
        output_jdict['mode'] = 'annotation'
        output_jdict['twconverted'] = '96E7D8C8-44E4-4055-8487-85B3208E51A2'
        output_jdict['template_version'] = "0.1"

        # output_jdict_imgs : 최종 산출물인 json 파일의 images의 value가 될 이미지 list
        output_jdict_imgs = list()

        # 전달받은 AIMMO 데이터의 경우, 별도의 image_id 정보가 존재하지만
        # GUID와 같이 unique한 문자열로 표현되어 있어서, 뷰어에서 오류를 발생할 수도 있기 때문에 id_idx 사용
        id_idx = 0

        # 전달받은 Annotation AI 데이터의 경우, 이미지 : 어노테이션 파일의 관계가 1 : 1이기 때문에
        # 어노테이션 파일 개수만큼 for loop를 수행해야 output_jdict의 images value를 얻어낼 수 있다.
        for each_jsonfile in anno_file_list:
            cur_img = dict()
            cur_img['image_id'] = str(id_idx)
            id_idx += 1

            with open(os.path.join(data_directory, each_jsonfile), 'r', encoding='utf-8') as jf:
                annotation_jdict = json.load(jf)

            cur_img['name'] = os.path.basename(annotation_jdict['filename'])
            cur_img['width'] = annotation_jdict['camera']['resolution_width']
            cur_img['height'] = annotation_jdict['camera']['resolution_height']

            # cur_img_objlist : 현재 이미지가 가지고 있는 객체('objects')의 value가 될 객체 list
            cur_img_objlist = list()

            for each_obj_info in annotation_jdict['annotations']:
                cur_obj = dict()

                shape_type = each_obj_info['type']

                # 전달받은 Annotation AI 데이터의 경우, 11개의 keypoint를 가지는 특이한 pose를 지원하기 때문에
                # keypoint는 변환 작업을 수행하지 않도록 if 분기문 사용
                if shape_type not in Annotation_AI_object_types.keys():
                    continue

                cur_obj['type'] = Annotation_AI_object_types[shape_type]
                cur_obj['label'] = each_obj_info['label']
                cur_obj['occluded'] = "0"
                cur_obj['z_order'] = "0"
                cur_obj['group_id'] = ""

                if shape_type == 'bbox':
                    xtl = each_obj_info['points'][0][0]
                    ytl = each_obj_info['points'][0][1]
                    xbr = each_obj_info['points'][2][0]
                    ybr = each_obj_info['points'][2][1]

                    position_value = str(xtl) + ', ' + str(ytl) + ', ' + str(xbr) + ', ' + str(ybr)

                # shape_type이 poly_seg인 경우
                else:
                    str_point_list = list()
                    for each_point in each_obj_info['points']:
                        str_point = str(each_point[0]) + ',' + str(each_point[1])
                        str_point_list.append(str_point)
                    position_value = ';'.join(str_point_list)

                cur_obj['position'] = position_value


                cur_obj_attrlist = list()

                for each_attr_key in each_obj_info['attributes']:
                    cur_attr = dict()
                    cur_attr['attribute_name'] = each_attr_key
                    cur_attr['attribute_value'] = each_obj_info['attributes'][each_attr_key]
                    cur_obj_attrlist.append(cur_attr)

                cur_obj['attributes'] = cur_obj_attrlist

                # 각 객체에 대한 처리가 완료되면, cur_img_objlist에 현재 객체(cur_obj)를 추가해준다.
                cur_img_objlist.append(cur_obj)

            cur_img['objects'] = cur_img_objlist

            # 현재 이미지(cur_img)에 대한 처리가 완료되면, output_jdict_imgs에 현재 이미지 관련 정보를 추가한다.
            output_jdict_imgs.append(cur_img)

        output_jdict['images'] = output_jdict_imgs

        # 최종 산출물일 dictionary 객체(output_jdict) 연산이 완료되면
        # 우선 원본 어노테이션 파일을 데이터 폴더\origin 폴더로 이동시켜서 원본 어노테이션 파일들(json)을 백업한다.
        for each_annofile in anno_file_list:
            shutil.move(os.path.join(data_directory, each_annofile), os.path.join(data_directory, 'origin'))

        fname, ext = os.path.splitext(anno_file_list[0])

        # 그리고나서, 첫 번째 원본 어노테이션 파일이름.json으로 데이터를 저장하면 작업이 완료된다.
        with open(os.path.join(data_directory, fname + '.json'), 'w', encoding='utf-8') as jf:
            json.dump(output_jdict, jf, indent=4, ensure_ascii=False)
