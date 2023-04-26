import os

import pandas as pd
import streamlit as st

from src.common.constants import (
    ADQ_WORKING_FOLDER,
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
from src.home import select_task
from src.models.data_labels import DataLabels
from src.models.projects_info import Project
from src.viewer.streamlit_img_label import st_img_label
from src.viewer.streamlit_img_label.image_manager import ImageManager


def _show_road_attributes(selected_shape: dict):
    shape_type = selected_shape["shapeType"]
    attributes_dict = selected_shape["attributes"]
    if shape_type == "spline":
        type1value = attributes_dict.get('type1', None)
        type2value = attributes_dict.get('type2', None)
        type3value = attributes_dict.get('type3', None)
        type4value = attributes_dict.get('type4', None)
        type5value = attributes_dict.get('type5', None)
        type6value = attributes_dict.get('type6', None)

        print("{} {}".format(type3value, Type3PositionE.get_index(type3value)))
        print("Type3 index value is {} ".format(Type3PositionE.get_all_types()[Type3PositionE.get_index(type3value)]))

        st.selectbox("1.Shape1(Q)", Type1Shape1Q.get_all_types(),
                     index=Type1Shape1Q.get_index(type1value) if type1value else 0)
        st.selectbox("2.Single/Double(W)", Type2SingleDoubleW.get_all_types(),
                     index=Type2SingleDoubleW.get_index(type2value) if type2value else 0)
        st.selectbox("3.Position(E)", Type3PositionE.get_all_types(),
                     index=Type3PositionE.get_index(type3value) if type3value else 0)
        st.selectbox("4.Unusual Case(R)", Type4UnusualCaseR.get_all_types(),
                     index=Type4UnusualCaseR.get_index(type4value) if type4value else 0)
        st.selectbox("5.Color(S)", Type5ColorS.get_all_types(),
                     index=Type5ColorS.get_index(type5value) if type5value else 0)
        st.selectbox("6.Bicycle(S)", Type6BicycleD.get_all_types(),
                     index=Type6BicycleD.get_index(type6value) if type6value else 0)
    elif shape_type == "boundary":
        type3value = attributes_dict.get('type3', None)
        boundary4value = attributes_dict.get('boundary', None)

        st.selectbox("3.Position(E)", Type3PositionE.get_all_types(),
                     index=Type3PositionE.get_index(type3value) if type3value else 0)
        st.selectbox("2.Boundary type(R)", BoundaryType2R.get_all_types(),
                     index=BoundaryType2R.get_index(boundary4value) if boundary4value else 0)

    elif shape_type == "polygon":
        type_value = attributes_dict.get('type', None)
        st.selectbox("1.Road marker type(Q)", TypeRoadMarkerQ.get_all_types(),
                     index=TypeRoadMarkerQ.get_index(type_value) if type_value else 0)


def main(selected_project: Project, error_codes=ErrorType.get_all_types()):
    selected_task, selected_index = select_task(selected_project.id)
    if selected_task:
        task_folder = os.path.join(ADQ_WORKING_FOLDER,
                                   str(selected_project.id),
                                   str(selected_task.id))
        data_labels = DataLabels.load(selected_task.anno_file_name)
        if not data_labels:
            st.warning("Data labels are empty")
            return

        image_filenames = [image.name for image in data_labels.images]

        if not st.session_state.get('image_index'):
            st.session_state["img_files"] = image_filenames
            st.session_state["image_index"] = 0
        else:
            st.session_state["img_files"] = image_filenames

        def refresh():
            data_labels.save(selected_task.anno_file_name)
            st.session_state["img_files"] = image_filenames
            st.session_state["image_index"] = 0

        def next_image():
            data_labels.save(selected_task.anno_file_name)
            image_index = st.session_state["image_index"]
            if image_index < len(st.session_state["img_files"]) - 1:
                st.session_state["image_index"] += 1
            else:
                st.warning('This is the last image.')

        def previous_image():
            data_labels.save(selected_task.anno_file_name)
            image_index = st.session_state["image_index"]
            if image_index > 0:
                st.session_state["image_index"] -= 1
            else:
                st.warning('This is the first image.')

        def go_to_image():
            data_labels.save(selected_task.anno_file_name)
            image_index = st.session_state["img_files"].index(st.session_state["img_file"])
            st.session_state["image_index"] = image_index

        def _pick_color(label: str, default_color: str) -> str:
            color_dict = {
                'boundary': 'blue',
                'spline': 'green',
                'polygon': 'purple'
            }

            return color_dict.get(label, default_color)

        # Sidebar: show status
        n_files = len(st.session_state["img_files"])
        st.sidebar.write("Total files:", n_files)
        st.sidebar.write("Current file: {}/{}".format(st.session_state["image_index"] + 1, n_files))

        st.sidebar.selectbox("Files",
                             st.session_state["img_files"],
                             index=st.session_state["image_index"],
                             on_change=go_to_image,
                             key="img_file")
        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.button(label="< Previous", on_click=previous_image)
        with col2:
            st.button(label="Next >", on_click=next_image)
        st.sidebar.button(label="Refresh", on_click=refresh)

        # Main content: review images
        image_index = st.session_state['image_index']

        im = ImageManager(task_folder, data_labels.images[image_index])
        resized_img = im.resizing_img()
        resized_shapes = im.get_resized_shapes()
        shape_color = _pick_color(resized_shapes[0].get('label'), 'green')

        st.markdown("#### {}".format(st.session_state['img_files'][image_index]))

        # Display cutout boxes
        selected_shape = st_img_label(resized_img, shape_color=shape_color, shape_props=resized_shapes)
        if selected_shape:
            selected_shape_id = selected_shape["shape_id"]
            # preview_img, preview_label = im.init_annotation(selected_shape)
            # if shape_id is new, it's an untagged label
            if selected_shape_id >= len(data_labels.images[image_index].objects):
                st.write("Untagged box added")
                selected_shape = im.upscale_shape(selected_shape)
                selected_shape['type'] = selected_shape['shapeType']
                del selected_shape['shapeType']
                print(selected_shape)
                untagged_object = DataLabels.Object.from_json(selected_shape)
                data_labels.images[image_index].objects.append(untagged_object)
            else:
                # print("accessing image_index {}, shape_id {}/{}".format(image_index, selected_shape_id,
                #                                                      len(data_labels.images[image_index]
                #                                        .objects)))
                if data_labels.images[image_index].objects[selected_shape_id].attributes:
                    df_attributes = pd.DataFrame.from_dict(data_labels.images[image_index]
                                                           .objects[selected_shape_id].attributes,
                                                           orient='index')
                else:
                    # print(data_labels.images[image_index]
                    #                                        .objects[selected_shape_id])
                    st.write(data_labels.images[image_index]
                                                           .objects[selected_shape_id])
                    # st.write(df_attributes.to_html(index=False, justify='center', classes='dataframe'), unsafe_allow_html=True)

                    # # Display the dataframe as an HTML table with custom styling using st.write()
                    # st.write(df_attributes.style.set_table_styles(
                    #     [{'selector': 'th', 'props': [('background', '#3366cc'), ('color', 'white'), ('text-align', 'center')]},
                    #      {'selector': 'td', 'props': [('text-align', 'center')]}])
                    #          .set_properties(**{'font-size': '12pt', 'border-collapse': 'collapse', 'border': '1px solid black'})
                    #          .to_html(), unsafe_allow_html=True)

            # if preview_img and preview_label:
            #     preview_img.thumbnail((200, 200))
            col1, col2, col3 = st.columns(3)
            with col1:
                # col1.image(preview_img)
                # st.write(preview_label)
                st.dataframe(selected_shape)
            with col2:
                print(selected_shape)
                _show_road_attributes(selected_shape)
            with col3:
                default_index = 0
                default_comment = None
                verification_result = im.image_labels.objects[selected_shape_id].verification_result
                if im.image_labels.objects[selected_shape_id].verification_result:
                    error_code = verification_result['error_code']
                    default_comment = verification_result.get('comment', None)
                    default_index = error_codes.index(error_code)

                select_label = col3.selectbox(
                    "Error", error_codes, key=f"error_{selected_shape_id}", index=default_index
                )
                comment = col3.text_input("Comment", default_comment)
                im.set_error(selected_shape_id, select_label, comment)

#
# if __name__ == "__main__":
#     main()
