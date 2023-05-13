import os.path
from base64 import b64encode

import streamlit as st
from PIL import Image

import src.viewer.app as app
from src.common.constants import SUPPORTED_IMAGE_FILE_EXTENSIONS
from src.common.logger import get_logger
from .home import (
    get_data_files,
    is_authenticated,
    login,
    logout,
    select_project,
    select_task)

logger = get_logger(__name__)


@st.cache_resource
def load_thumbnail(file_path):
    with Image.open(file_path) as image:
        return image.copy()


def show_images(project_folder):
    thumbnail_filenames = get_data_files(project_folder, is_thumbnails=True)
    logger.info(f"{project_folder} {thumbnail_filenames}")
    # Define the number of columns
    num_columns = 5

    columns = st.columns(num_columns)
    for i, file in enumerate(thumbnail_filenames["."]):
        with columns[i % num_columns]:
            thumbnail_image = load_thumbnail(file)
            st.image(thumbnail_image, width=100)
            truncated_name = os.path.basename(file)[:20] + "..." if len(
                os.path.basename(file)) > 20 else os.path.basename(file)
            if st.button(truncated_name, key=f'{truncated_name}_{i}'):
                full_size_filename = os.path.join(project_folder, "data", os.path.basename(file))
                full_size_image = Image.open(full_size_filename)
                st.image(full_size_image, caption="Full-size Image")


def review_images():
    selected_project = select_project(is_sidebar=True)
    if selected_project:
        show_images(selected_project.dir_name)


def review_task():
    selected_project = select_project(is_sidebar=True)
    if selected_project:
        selected_task = select_task(selected_project.id)
        if selected_task:
            if selected_project.extended_properties:
                review_model_task(selected_task)
            else:
                # # Navigate to a new page with the task details
                # st.experimental_set_query_params(task_id=selected_task.id)
                app.main(selected_task)


def compare_tasks():
    selected_project = select_project(is_sidebar=True)
    if selected_project:
        task1 = select_task(selected_project.id, label="Select task1")
        task2 = select_task(selected_project.id, label="Select task2")

        if task1 and task2:
            col1, col2 = st.columns(2)

            with col1:
                app.main(task1)
            with col2:
                app.main(task2, is_second_viewer=True)


def review_model_task(selected_task):
    if selected_task.data_files and len(selected_task.data_files) > 0:
        for folder, files in selected_task.data_files.items():
            for file in files:
                st.write("📄{}".format(file))
                basename, extension = os.path.splitext(file)
                if extension.lower() == ".pdf":
                    pdf_file = open(os.path.join(folder, file), "rb").read()
                    # Embed the PDF file in an iframe
                    pdf_url = "data:application/pdf;base64," + b64encode(pdf_file).decode("utf-8")
                    st.write(f'<iframe src="{pdf_url}" width="700" height="1000"></iframe>', unsafe_allow_html=True)
                elif extension.lower() in SUPPORTED_IMAGE_FILE_EXTENSIONS:
                    st.image(os.path.join(folder, file))
                elif extension.lower() in [".docx", ".doc"]:
                    word_file = open(os.path.join(folder, file), "rb").read()
                    # Embed the Word document in an iframe using HTML tags
                    word_url = "data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64," + b64encode(
                        word_file).decode("utf-8")
                    st.markdown(f'<iframe https://view.officeapps.live.com/op/embed.aspx?src="{word_url}" width="700" height="1000"></iframe>', unsafe_allow_html=True)
    else:
        st.write("No uploaded files to review")


def main():
    # Clear the sidebar
    st.sidebar.empty()
    # Clear the main page
    st.empty()

    menu = {
        "Review Images": lambda: review_images(),
        "Review Task": lambda: review_task(),
        "Compare Tasks": lambda: compare_tasks(),
    }

    # Create a sidebar with menu options
    selected_action = st.sidebar.radio("Choose action", list(menu.keys()))

    if selected_action:
        # Call the selected method based on the user's selection
        menu[selected_action]()


if __name__ == '__main__':
    if not is_authenticated():
        login()
    else:
        main()
        logout()
