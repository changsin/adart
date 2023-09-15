import os

import pandas as pd
import streamlit as st

from src.common.constants import (
    ErrorType,
    Type1Shape1Q,
    Type2SingleDoubleW,
    Type3PositionE,
    Type4UnusualCaseR,
    Type5ColorS,
    Type6BicycleD,
    BoundaryType2R,
    TypeRoadMarkerQ
)
from src.common.logger import get_logger
from src.models.data_labels import DataLabels
from src.models.tasks_info import Task
from src.viewer import st_img_label
from src.viewer.image_manager import ImageManager

logger = get_logger(__name__)

DEFAULT_SHAPE_COLOR = "magenta"
min_width = 700
max_width = 1000


def _display_type_attributes(selected_shape: dict, key="1"):
    shape_type = selected_shape["shapeType"]
    attributes_dict = selected_shape["attributes"]
    if shape_type == "box":
        if attributes_dict:
            st.dataframe(pd.DataFrame.from_dict(attributes_dict, orient='index'))
    elif shape_type == "spline":
        type1value = attributes_dict.get('type1', None)
        type2value = attributes_dict.get('type2', None)
        type3value = attributes_dict.get('type3', None)
        type4value = attributes_dict.get('type4', None)
        type5value = attributes_dict.get('type5', None)
        type6value = attributes_dict.get('type6', None)

        st.selectbox("1.Shape1(Q)", Type1Shape1Q.get_all_types(),
                     key=f"1.Shape1(Q){key}",
                     index=Type1Shape1Q.get_index(type1value) if type1value else 0)
        st.selectbox("2.Single/Double(W)", Type2SingleDoubleW.get_all_types(),
                     key=f"2.Single/Double(W){key}",
                     index=Type2SingleDoubleW.get_index(type2value) if type2value else 0)
        st.selectbox("3.Position(E)", Type3PositionE.get_all_types(),
                     key=f"3.Position(E){key}",
                     index=Type3PositionE.get_index(type3value) if type3value else 0)
        st.selectbox("4.Unusual Case(R)", Type4UnusualCaseR.get_all_types(),
                     key=f"4.Unusual Case(R){key}",
                     index=Type4UnusualCaseR.get_index(type4value) if type4value else 0)
        st.selectbox("5.Color(S)", Type5ColorS.get_all_types(),
                     key=f"5.Color(S){key}",
                     index=Type5ColorS.get_index(type5value) if type5value else 0)
        st.selectbox("6.Bicycle(S)", Type6BicycleD.get_all_types(),
                     key=f"6.Bicycle(S){key}",
                     index=Type6BicycleD.get_index(type6value) if type6value else 0)
    elif shape_type == "boundary":
        type3value = attributes_dict.get('type3', None)
        boundary4value = attributes_dict.get('boundary', None)

        st.selectbox("3.Position(E)", Type3PositionE.get_all_types(),
                     key=f"3.Position(E){key}",
                     index=Type3PositionE.get_index(type3value) if type3value else 0)
        st.selectbox("2.Boundary type(R)", BoundaryType2R.get_all_types(),
                     key=f"2.Boundary type(R){key}",
                     index=BoundaryType2R.get_index(boundary4value) if boundary4value else 0)

    elif shape_type == "polygon":
        type_value = attributes_dict.get('type', None)
        st.selectbox("1.Road marker type(Q)", TypeRoadMarkerQ.get_all_types(),
                     key=f"1.Road marker type(Q){key}",
                     index=TypeRoadMarkerQ.get_index(type_value) if type_value else 0)


def main(selected_task: Task, is_second_viewer=False, error_codes=ErrorType.get_all_types()):
    def save(image_index: int, im: ImageManager):
        image_to_save = im.to_data_labels_image()

        curr_image = data_labels.images[image_index]
        if curr_image.name == image_to_save.name:
            data_labels.images[image_index] = image_to_save
        else:
            data_labels.save_image(image_to_save)

        data_labels.save(selected_task.anno_file_name)
        selected_task.error_count = data_labels.get_verification_result_sum()
        selected_task.save()

    def refresh():
        save(st.session_state["image_index"], im)

    def previous_image():
        save(st.session_state["image_index"], im)
        if st.session_state["image_index"] > 0:
            st.session_state["image_index"] -= 1
        else:
            st.warning('This is the first image.')

    def next_image():
        save(st.session_state["image_index"], im)
        if st.session_state["image_index"] < len(st.session_state["img_files"]) - 1:
            st.session_state["image_index"] += 1
        else:
            st.warning('This is the last image.')

    def go_to_image():
        save(st.session_state["image_index"], im)
        selected_option = st.session_state["img_file"]
        image_index = st.session_state["img_files"].index(selected_option.split(") ")[-1])
        st.session_state["image_index"] = image_index

    def viewer_menu(im: ImageManager):
        st.markdown(
            """
            <style>
            .label-container > div:first-child {
                display: inline-block;
                width: 150px;
                padding-right: 10px;
                vertical-align: top;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        # Sidebar: show status
        n_files = len(st.session_state["img_files"])
        # Main content: review images
        image_index = st.session_state['image_index']

        if image_index >= n_files:
            st.session_state['image_index'] = 0
            image_index = 0

        # Modify the select_box to include the file index prefix
        select_box_options = [f"({i + 1}/{n_files}) {filename}" for i, filename in enumerate(st.session_state["img_files"])]

        col1, col2, col3, col4, col5 = st.columns([1, 6, 1, 1, 1])
        with col1:
            st.markdown('<div class="label-container"></div>', unsafe_allow_html=True)
            st.button(label=":arrow_backward:", on_click=previous_image)

        with col2:
            st.markdown('<div class="label-container">', unsafe_allow_html=True)
            st.selectbox("",
                         select_box_options,
                         index=st.session_state["image_index"],
                         on_change=go_to_image,
                         key="img_file",
                         label_visibility="collapsed")
            st.markdown('</div>', unsafe_allow_html=True)

        with col3:
            st.markdown('<div class="label-container"></div>', unsafe_allow_html=True)
            st.button(label=":arrow_forward:", on_click=next_image)

        with col4:
            st.markdown('<div class="label-container"></div>', unsafe_allow_html=True)
            st.button(label="**Save**", on_click=refresh)

        selected_shape = call_frontend(im, image_index)
        with col5:
            if selected_shape:
                logger.info(f"***Received {selected_shape}")
                scaled_shape = process_selected_shape(selected_shape)
                if scaled_shape is None:
                    return image_index

                selected_shape_id = scaled_shape["shape_id"]
                im_selected_shape = im.get_shape_by_id(selected_shape_id)
                if scaled_shape.get("verification_result") or im_selected_shape.get("verification_result"):
                    verification_result_dict = scaled_shape.get("verification_result")
                    im.set_review(selected_shape_id,
                                  verification_result_dict["error_code"],
                                  verification_result_dict.get("comment", None))
                    save(image_index, im)

                # # present 3 columns for the selected shape
                # selected_shape_id = selected_shape['shape_id']
                # key = f"{selected_shape_id}_{is_second_viewer}"

                # # thumbnail image
                # with col1:
                #     preview_img = im.get_preview_thumbnail(scaled_shape)
                #     if preview_img:
                #         preview_img.thumbnail((200, 200))
                #         col1.image(preview_img)
                #         st.write(scaled_shape["label"])
                #     points = selected_shape["points"]
                #     st.dataframe(pd.DataFrame(points))

                # # attributes
                # with col2:
                #     _display_type_attributes(selected_shape, key=key)

                # verification result
                # with col4:
                # default_index = 0
                # verification_result = im.get_shape_by_id(selected_shape_id)['verification_result']
                # if verification_result:
                #     error_code = verification_result['error_code']
                #     default_index = error_codes.index(error_code)
                #
                # comment = ""
                # st.markdown('<div class="label-container"></div>', unsafe_allow_html=True)
                # select_label = st.selectbox(":red[Error]",
                #                             error_codes,
                #                             key=f"error_{selected_shape_id}_{key}",
                #                             index=default_index)
                # if select_label:
                #     if not verification_result:
                #         verification_result = dict()
                #     default_comment = verification_result.get('comment', "")
                #     comment = st.text_input("", default_comment, key={key},
                #                             label_visibility="collapsed")
                #
                # # save the verification result
                # im.set_review(selected_shape_id, select_label, comment)
                #
                # if verification_result and verification_result['error_code'] == 'Untagged':
                #     delete_shape = st.button(":red[Delete]", key=key)
                #     if delete_shape:
                #         im.remove_shape(selected_shape)
                #         logger.info(f"Deleted {selected_shape}")
                #
                # save(image_index, im)

        return image_index

    def call_frontend(im: ImageManager, image_index: int) -> dict:
        window_width = st.session_state.get("window_width", 700)
        logger.info(f"window_width: {window_width}")
        max_width = window_width * 0.7 if window_width > 700 else 700
        min_width = window_width * 0.6 if window_width > 700 else 700
        logger.info(f"min_width, max_width = {min_width}, {max_width}")
        resized_img = im.resizing_img(min_width=min_width, max_width=max_width)
        resized_shapes = im.get_downscaled_shapes()
        shape_color = DEFAULT_SHAPE_COLOR

        if resized_img:
            return st_img_label(resized_img, shape_color=shape_color, shape_props=resized_shapes,
                                key=f"{image_index}_2" if is_second_viewer else f"{image_index}_1")
        else:
            st.write("Image file not found")

    def process_selected_shape(selected_shape: dict):
        scaled_shape = im.upscale_shape(selected_shape)
        selected_shape_id = selected_shape["shape_id"]
        # if shape_id is new, it's an untagged label
        if not im.get_shape_by_id(selected_shape_id):
            im.add_shape(scaled_shape)

        # if deleted in the frontend, delete here too
        attributes = scaled_shape.get("attributes")
        if attributes:
            status = attributes.get("status")
            if status and status == "DELETED":
                im.remove_shape(scaled_shape)
                logger.info(f"DELETED {scaled_shape}")
                return None

        return scaled_shape

    def _pick_color(label: str, default_color: str) -> str:
        color_dict = {
            'boundary': 'blue',
            'spline': 'green',
            'polygon': 'purple'
        }
        return color_dict.get(label, default_color)

    # Load up the image and the labels
    if selected_task.anno_file_name:
        data_labels = DataLabels.load(selected_task.anno_file_name)
        if not data_labels:
            st.warning("Data labels are empty")
            return

    # set session states
    image_filenames = [os.path.join(f"data", image.name) for image in data_labels.images]
    if not st.session_state.get('image_index'):
        st.session_state["img_files"] = image_filenames
        st.session_state["image_index"] = 0
    else:
        st.session_state["img_files"] = image_filenames

    image_index = st.session_state["image_index"]
    task_folder = os.path.dirname(selected_task.anno_file_name)
    image_filename = os.path.join(task_folder, image_filenames[image_index])
    im = ImageManager(image_filename, data_labels.images[image_index])

    # call the frontend
    if not is_second_viewer:
        image_index = viewer_menu(im)


#
# if __name__ == "__main__":
#     main()
