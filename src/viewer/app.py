import os

import pandas as pd
import streamlit as st

from src.common.constants import ADQ_WORKING_FOLDER, ErrorType
from src.home import select_task
from src.models.data_labels import DataLabels
from src.models.projects_info import Project
from src.viewer.streamlit_img_label import st_img_label
from src.viewer.streamlit_img_label.image_manager import DartImageManager


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

        im = DartImageManager(task_folder, data_labels.images[image_index])
        resized_img = im.resizing_img()
        resized_shapes = im.get_resized_shapes()
        shape_color = _pick_color(resized_shapes[0].get('label'), 'green')

        st.markdown("#### {}".format(st.session_state['img_files'][image_index]))

        # Display cutout boxes
        selected_shape = st_img_label(resized_img, shape_color=shape_color, shape_props=resized_shapes)
        if selected_shape:
            preview_imgs = [im.init_annotation(selected_shape)]

            if len(preview_imgs) > 0:
                for i, prev_img in enumerate(preview_imgs):
                    prev_img[0].thumbnail((200, 200))
                    col1, col2 = st.columns(2)
                    with col1:
                        col1.image(prev_img[0])
                        st.dataframe(selected_shape)
                    with col2:
                        default_index = 0
                        if im.image_labels.objects[i].verification_result:
                            error_code = im.image_labels.objects[i].verification_result['error_code']
                            default_index = error_codes[error_code]

                        select_label = col2.selectbox(
                            "Error", error_codes, key=f"error_{i}", index=default_index
                        )
                        if select_label:
                            print("verification_result {}".format(im.image_labels.objects[i].verification_result))
                            im.set_annotation(i, select_label)

            selected_shape_id = selected_shape["shape_id"]
            if selected_shape_id > len(data_labels.images[image_index].objects) - 1:
                st.write("Untagged box added")
                print(selected_shape)
                untagged_dict = dict()
                untagged_dict['label'] = selected_shape['label']
                untagged_dict['type'] = selected_shape['shapeType']
                untagged_dict['points'] = selected_shape['points']
                untagged_dict['verification_result'] = dict()
                untagged_dict['verification_result']['name'] = selected_shape['label']
                untagged_object = DataLabels.Object.from_json(untagged_dict)
                data_labels.images[image_index].objects.append(untagged_object)
            elif data_labels.images[image_index].objects[selected_shape_id].attributes:
                df_attributes = pd.DataFrame.from_dict(data_labels.images[image_index]
                                                       .objects[selected_shape_id].attributes,
                                                       orient='index')
                # st.write(df_attributes.to_html(index=False, justify='center', classes='dataframe'), unsafe_allow_html=True)

                # Display the dataframe as an HTML table with custom styling using st.write()
                st.write(df_attributes.style.set_table_styles(
                    [{'selector': 'th', 'props': [('background', '#3366cc'), ('color', 'white'), ('text-align', 'center')]},
                     {'selector': 'td', 'props': [('text-align', 'center')]}])
                         .set_properties(**{'font-size': '12pt', 'border-collapse': 'collapse', 'border': '1px solid black'})
                         .to_html(), unsafe_allow_html=True)
        # else:
        #     df_attributes = pd.DataFrame(data_labels.images[st.session_state["image_index"]].to_json())
        #     st.write(df_attributes.to_html(index=False, justify='center', classes='dataframe'), unsafe_allow_html=True)

#
# if __name__ == "__main__":
#     main()
