import datetime as dt
import os.path
from base64 import b64encode

import streamlit as st

import src.viewer.app as app
from src.common import utils
from src.common.constants import SUPPORTED_IMAGE_FILE_EXTENSIONS
from .home import (
    is_authenticated,
    login,
    logout,
    select_project,
    select_task)


def _show_full_size_image(full_path, size, date):
    st.image(full_path,
             # use_column_width=True,
             caption="{} {} {}".format(os.path.basename(full_path),
                                       size,
                                       date))


@st.cache_resource
def show_images(files_dict: dict):
    # Define the number of columns
    num_columns = 5

    for folder, files in files_dict.items():
        # # Calculate the number of rows needed based on the number of images and columns
        # num_rows = int(len(files) / num_columns) + (1 if len(files) % num_columns > 0 else 0)

        # Create a layout with the specified number of columns
        columns = st.columns(num_columns)
        for i, file in enumerate(files):
            with columns[i % num_columns]:
                full_path = os.path.join(folder, file)
                file_stat = os.stat(full_path)
                dt_datetime = dt.datetime.fromtimestamp(file_stat.st_ctime)
                st.image(full_path,
                         # use_column_width=True,
                         # title="{} {} {}".format(file,
                         #                           utils.humanize_bytes(file_stat.st_size),
                         #                           dt_datetime.date()),
                         width=100)
                # button_clicked = st.button("click to expand {}".format(file))
                # Call the event handler if the button is clicked
                # Create the expander panel
                with st.expander("{}".format(file)):
                    # # Call the event handler if the button is clicked
                    # if button_clicked:
                    _show_full_size_image(full_path,
                                          utils.humanize_bytes(file_stat.st_size),
                                          dt_datetime.date())


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
