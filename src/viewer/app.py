import os

import streamlit as st

from src.common.constants import ADQ_WORKING_FOLDER, ErrorType
from src.home import select_task
from src.models.projects_info import Project
from src.pages.metrics import load_label_file
from src.viewer.streamlit_img_label import st_img_label
from src.viewer.streamlit_img_label.image_manager import DartImageManager
import pandas as pd


def main(selected_project: Project, labels=ErrorType.get_all_types()):
    selected_task, selected_index = select_task(selected_project.id)
    if selected_task:
        task_folder = os.path.join(ADQ_WORKING_FOLDER,
                                   str(selected_project.id),
                                   str(selected_task.id))
        dart_labels = load_label_file(task_folder,
                                      os.path.basename(selected_task.anno_file_name))
        image_filenames = [image.name for image in dart_labels.images]

        if not st.session_state.get('image_index'):
            st.session_state["img_files"] = image_filenames
            st.session_state["image_index"] = 0
        else:
            st.session_state["img_files"] = image_filenames

        def refresh():
            st.session_state["img_files"] = image_filenames
            st.session_state["image_index"] = 0

        def next_image():
            image_index = st.session_state["image_index"]
            if image_index < len(st.session_state["img_files"]) - 1:
                st.session_state["image_index"] += 1
            else:
                st.warning('This is the last image.')

        def previous_image():
            image_index = st.session_state["image_index"]
            if image_index > 0:
                st.session_state["image_index"] -= 1
            else:
                st.warning('This is the first image.')

        def next_annotate_file():
            image_index = st.session_state["image_index"]
            next_image_index = image_index + 1 if (image_index < len(image_filenames) - 1) else image_index
            if next_image_index != image_index:
                st.session_state["image_index"] = next_image_index
            else:
                st.warning("All images are annotated.")
                next_image()

        def go_to_image():
            image_index = st.session_state["img_files"].index(st.session_state["img_file"])
            st.session_state["image_index"] = image_index

        def pick_color(label: str, default_color: str) -> str:
            color_dict = {
                'boundary': 'blue',
                'spline': 'green',
                'polygon': 'purple'
            }

            return color_dict.get(label, default_color)

        # Sidebar: show status
        n_files = len(st.session_state["img_files"])
        st.sidebar.write("Total files:", n_files)

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
        st.sidebar.button(label="Next image to review", on_click=next_annotate_file)
        st.sidebar.button(label="Refresh", on_click=refresh)

        # Main content: review images
        image_index = st.session_state['image_index']

        im = DartImageManager(task_folder, dart_labels.images[image_index])
        resized_img = im.resizing_img()
        resized_shapes = im.get_resized_shapes()
        shape_color = pick_color(resized_shapes[0].get('label'), 'red')

        st.markdown("### {} {}".format(image_index, st.session_state['img_files'][image_index]))
        shapes = st_img_label(resized_img, shape_color=shape_color, shape_props=resized_shapes)

        if dart_labels.images[image_index].objects[0].attributes:
            df_attributes = pd.DataFrame.from_dict(dart_labels.images[st.session_state["image_index"]]
                                                   .objects[0].attributes,
                                                   orient='index')

            # Display the dataframe as an HTML table with custom styling using st.write()
            st.write(df_attributes.style.set_table_styles(
                [{'selector': 'th', 'props': [('background', '#3366cc'), ('color', 'white'), ('text-align', 'center')]},
                 {'selector': 'td', 'props': [('text-align', 'center')]}])
                     .set_properties(**{'font-size': '12pt', 'border-collapse': 'collapse', 'border': '1px solid black'})
                     .to_html(), unsafe_allow_html=True)
        else:
            df_attributes = pd.DataFrame(dart_labels.images[st.session_state["image_index"]])
            st.write(df_attributes.to_html(index=False, justify='center', classes='dataframe'), unsafe_allow_html=True)

        if shapes:
            preview_imgs = im.init_annotation(shapes)

            for i, prev_img in enumerate(preview_imgs):
                prev_img[0].thumbnail((200, 200))
                col1, col2 = st.columns(2)
                with col1:
                    col1.image(prev_img[0])
                with col2:
                    default_index = 0

                    select_label = col2.selectbox(
                        "Error", labels, key=f"error_{i}", index=default_index
                    )
                    im.set_annotation(i, select_label)

#
# if __name__ == "__main__":
#     main()
