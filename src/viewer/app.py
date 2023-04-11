import os

import streamlit as st

from src.common.constants import ADQ_WORKING_FOLDER, ErrorType
from src.home import select_project, select_task
from src.pages.metrics import load_label_file
from src.viewer.streamlit_img_label import st_img_label
from src.viewer.streamlit_img_label.image_manager import DartImageManager, DartImageDirManager


def main(labels=ErrorType.get_all_types()):
    selected_project = select_project(is_sidebar=True)
    if not selected_project:
        return

    if selected_project.extended_properties:
        st.sidebar.write("Not a data project")
        return

    selected_task, selected_index = select_task(selected_project.id)
    if selected_task:
        task_folder = os.path.join(ADQ_WORKING_FOLDER,
                                   str(selected_project.id),
                                   str(selected_index))
        dart_labels = load_label_file(task_folder, selected_task.anno_file_name)

        # TODO: find the mapping between the img_dir and dart_labels
        data_files_list = list(selected_project.data_files.items())
        img_dir = data_files_list[selected_index][0]

        idm = DartImageDirManager(img_dir, dart_labels)

        if "img_files" not in st.session_state:
            st.session_state["img_files"] = idm.get_all_img_files()
            st.session_state["annotation_files"] = idm.get_exist_annotation_files()
            st.session_state["image_index"] = 0
            st.session_state["annotation_file_index"] = 0
        else:
            idm.set_all_img_files(st.session_state["img_files"])
            idm.set_annotation_files(st.session_state["annotation_files"])

        def refresh():
            st.session_state["img_files"] = idm.get_all_img_files()
            st.session_state["annotation_files"] = idm.get_exist_annotation_files()
            st.session_state["image_index"] = 0
            st.session_state["annotation_file_index"] = 0

        def next_image():
            image_index = st.session_state["image_index"]
            if image_index < len(st.session_state["img_files"]) - 1:
                st.session_state["image_index"] += 1
                st.session_state["annotation_file_index"] += 1
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
            next_image_index = idm.get_next_annotation_image(image_index)
            if next_image_index:
                st.session_state["image_index"] = idm.get_next_annotation_image(image_index)
            else:
                st.warning("All images are annotated.")
                next_image()

        def go_to_image():
            file_index = st.session_state["img_files"].index(st.session_state["img_file"])
            st.session_state["image_index"] = file_index

        # Sidebar: show status
        n_files = len(st.session_state["img_files"])
        n_annotate_files = len(st.session_state["annotation_files"])
        st.sidebar.write("Total files:", n_files)
        st.sidebar.write("Total annotate files:", n_annotate_files)
        st.sidebar.write("Remaining files:", n_files - n_annotate_files)

        st.sidebar.selectbox(
            "Files",
            st.session_state["img_files"],
            index=st.session_state["image_index"],
            on_change=go_to_image,
            key="img_file",
        )
        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.button(label="< Previous", on_click=previous_image)
        with col2:
            st.button(label="Next >", on_click=next_image)
        st.sidebar.button(label="Next need annotate", on_click=next_annotate_file)
        st.sidebar.button(label="Refresh", on_click=refresh)

        # Main content: annotate images
        img_file_name = idm.get_image(st.session_state["image_index"])
        # img_path = os.path.join(img_dir, img_file_name)
        im = DartImageManager(img_dir, dart_labels.images[st.session_state["image_index"]])
        img = im.get_img()
        resized_img = im.resizing_img()
        resized_rects = im.get_resized_rects()
        rects = st_img_label(resized_img, box_color="red", rects=resized_rects)

        def annotate():
            im.save_annotation()
            image_annotate_file_name = img_file_name.split(".")[0] + ".xml"
            if image_annotate_file_name not in st.session_state["annotation_files"]:
                st.session_state["annotation_files"].append(image_annotate_file_name)
            next_annotate_file()

        if rects:
            st.button(label="Save", on_click=annotate)
            preview_imgs = im.init_annotation(rects)

            for i, prev_img in enumerate(preview_imgs):
                prev_img[0].thumbnail((200, 200))
                col1, col2 = st.columns(2)
                with col1:
                    col1.image(prev_img[0])
                with col2:
                    default_index = 0
                    # print(prev_img)
                    # if prev_img[1]:
                    #     default_index = labels.index(prev_img[1])

                    select_label = col2.selectbox(
                        "Error", labels, key=f"error_{i}", index=default_index
                    )
                    im.set_annotation(i, select_label)


if __name__ == "__main__":
    main()
