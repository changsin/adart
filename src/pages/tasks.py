import copy
import datetime as dt
import importlib.util
import json
import os.path
import random
import shutil
from base64 import b64encode

import pandas as pd
import streamlit as st

spec = importlib.util.find_spec("src")
if spec is None:
    import sys
    from pathlib import Path

    path_root = Path(__file__).parents[2]
    sys.path.append(str(path_root))

import src.viewer.app as app
from src.common import utils
from src.common.constants import (
    ADQ_WORKING_FOLDER,
    SUPPORTED_IMAGE_FILE_EXTENSIONS,
    SUPPORTED_LABEL_FORMATS,
    CVAT_XML,
    STRADVISION_XML,
    GPR_JSON,
    ModelTaskType)
from src.common.convert_lib import (
    convert_CVAT_to_Form,
    from_gpr_json,
    from_strad_vision_xml)
from src.home import (
    is_authenticated,
    login,
    logout,
    select_project,
    select_task)
from src.models.data_labels import DataLabels
from src.models.projects_info import Project
from src.models.tasks_info import Task, TasksInfo, TaskState

DATE_FORMAT = "%Y %B %d %A"
LABEL_FILE_EXTENSIONS = ['json', 'xml']


def calculate_sample_count(count, percent):
    return int((count * percent) / 100)


def calculate_sample_distribution(df_total_count: pd.DataFrame,
                                  sample_percent: int) -> pd.DataFrame:
    df_sample_count = df_total_count.copy()

    for index, row in df_total_count.iterrows():
        sample_count = calculate_sample_count(row['count'], sample_percent)
        if sample_count < 1.0:
            st.warning("Please set a higher percentage to pick at least one file per folder")
            return None
        else:
            df_sample_count.iloc[index] = (row['filename'], sample_count)

    return df_sample_count


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


def sample_data(selected_project: Project, dart_labels_dict: dict, df_sample_count: pd.DataFrame):
    sampled = {}
    for index, row in df_sample_count.iterrows():
        label_filename = row['filename']
        sample_count = row['count']

        dart_labels = dart_labels_dict[label_filename]
        sampled_dart_labels = copy.deepcopy(dart_labels)
        random.shuffle(sampled_dart_labels.images)

        sampled_dart_labels.images = sampled_dart_labels.images[:sample_count]
        sampled[label_filename] = sampled_dart_labels

        # save the sample label file
        task_folder = os.path.join(ADQ_WORKING_FOLDER, str(selected_project.id), str(index))
        if not os.path.exists(task_folder):
            os.mkdir(task_folder)
        utils.to_file(json.dumps(sampled_dart_labels, default=utils.default, indent=2),
                      os.path.join(task_folder, label_filename))

        tasks_info = TasksInfo.get_tasks_info()
        task_id = tasks_info.get_next_task_id()
        task_name = "{}-{}-{}".format(selected_project.id, task_id, label_filename)
        new_task = Task(task_id,
                        task_name,
                        selected_project.id,
                        str(TaskState.DVS_NEW.description),
                        label_filename)

        tasks_info.add(new_task)
        tasks_info.save()

    return sampled


def create_data_tasks(selected_project: Project):
    if len(selected_project.label_files) > 0:
        data_labels = DataLabels.load(selected_project.label_files)
        images_per_label_file_dict = dict()
        if data_labels:
            for labels_file, dart_labels in data_labels.images():
                images_per_label_file_dict[labels_file] = len(dart_labels.images)

        df_total_count = pd.DataFrame(images_per_label_file_dict.items(), columns=['filename', 'count'])
        df_total_count['filename'] = df_total_count['filename'].apply(lambda file: os.path.basename(file))
        st.dataframe(df_total_count)

        with st.form("Create Tasks"):
            sample_percent = st.number_input("% of samples", step=utils.step_size(0.0), format="%.2f")
            is_keep_folders = st.checkbox("Keep folder structures", value=True)

            submitted = st.form_submit_button("Create tasks")
            if submitted:
                if sample_percent <= 0:
                    st.warning("Please enter a valid percent value")
                    return
                else:
                    st.write("Alright")
                    total_count = df_total_count['count'].sum()
                    total_sample_count = calculate_sample_count(total_count, sample_percent)

                    if is_keep_folders:
                        df_sample_count = calculate_sample_distribution(df_total_count, sample_percent)
                        if df_sample_count is None:
                            return

                        total_sample_count = df_sample_count['count'].sum()

                    if total_sample_count > total_count:
                        st.warning("Please enter a valid percent value.")
                        st.warning("Sample count ({}) is greater than the total image count ({})"
                                   .format(total_sample_count, total_count))
                        st.dataframe(df_sample_count)
                        return

                    st.write("Here is how the image files are sampled")
                    st.dataframe(df_sample_count)

                    sample_data(selected_project, data_labels.to_json(), df_sample_count)


def assign_tasks():
    selected_project = select_project()
    if selected_project:
        tasks = TasksInfo.get_tasks(selected_project.id)
        st.checkbox("Assign tasks", )
        df_tasks = pd.DataFrame(tasks)
        st.dataframe(df_tasks)


def add_task():
    selected_project = select_project()
    if selected_project:
        if selected_project.extended_properties:
            add_model_task(selected_project)
        else:
            add_data_task(selected_project)


def add_data_task(selected_project: Project):
    with st.form("Add Data Task"):
        task_name = st.text_input("**Task Name:**")
        options = [SUPPORTED_IMAGE_FILE_EXTENSIONS]
        selected_file_types = st.selectbox("**Image file types**",
                                           options,
                                           index=len(options) - 1)
        uploaded_data_files = st.file_uploader("Upload data files",
                                               selected_file_types,
                                               accept_multiple_files=True)

        uploaded_label_files = st.file_uploader("Upload label files",
                                                LABEL_FILE_EXTENSIONS,
                                                accept_multiple_files=True)

        tasks_info = TasksInfo.get_tasks_info()
        new_task_id = tasks_info.get_next_task_id()

        save_folder = os.path.join(ADQ_WORKING_FOLDER, str(selected_project.id), str(new_task_id))
        if not os.path.exists(save_folder):
            os.mkdir(save_folder)

        data_files = dict()
        if uploaded_data_files:
            # Save the uploaded files
            saved_filenames = []
            for file in uploaded_data_files:
                with open(os.path.join(save_folder, file.name), "wb") as f:
                    f.write(file.getbuffer())
                saved_filenames.append(file.name)
            data_files[save_folder] = saved_filenames

        labels_format_type = st.selectbox("**Choose format:**", SUPPORTED_LABEL_FORMATS)
        if uploaded_label_files:
            # Save the uploaded files in origin folder
            ori_folder = os.path.join(save_folder, "origin")
            if not os.path.exists(ori_folder):
                os.mkdir(ori_folder)

            saved_filenames = []
            for file in uploaded_label_files:
                with open(os.path.join(ori_folder, file.name), "wb") as f:
                    f.write(file.getbuffer())
                saved_filenames.append(os.path.join(ori_folder, file.name))

            saved_filenames.sort()
            if labels_format_type == STRADVISION_XML:
                converted_filename = from_strad_vision_xml("11", saved_filenames, save_folder)
            elif labels_format_type == CVAT_XML:
                # There should be only 1 per folder
                converted_filename = convert_CVAT_to_Form("NN", saved_filenames[0], save_folder)
            elif labels_format_type == GPR_JSON:
                converted_filename = from_gpr_json("11", saved_filenames, save_folder)

        # label_files[save_folder] = [converted_filename]
        submitted = st.form_submit_button("Add Data Task")
        if submitted:
            new_task = Task(new_task_id, task_name, selected_project.id, "Created",
                            date=str(dt.datetime.now()),
                            anno_file_name=converted_filename)
            tasks_info.add(new_task)
            tasks_info.save()

            st.markdown("### Task ({}) ({}) added to Project ({})".format(new_task_id, task_name, selected_project.id))


def add_model_task(selected_project: Project):
    with st.form("Add a Model Task"):
        task_name = st.text_input("**Task Name:**")
        description = st.text_area("Description")
        date = st.date_input("**Date:**")
        task_stage = st.selectbox("Task type", ModelTaskType.get_all_types())

        uploaded_files = st.file_uploader("Upload artifacts", accept_multiple_files=True)

        tasks_info = TasksInfo.get_tasks_info()
        new_task_id = tasks_info.get_next_task_id()

        save_folder = os.path.join(ADQ_WORKING_FOLDER, str(selected_project.id), str(new_task_id))
        if not os.path.exists(save_folder):
            os.mkdir(save_folder)

        data_files = dict()
        if uploaded_files:
            # Save the uploaded file
            saved_filenames = []
            for file in uploaded_files:
                with open(os.path.join(save_folder, file.name), "wb") as f:
                    f.write(file.getbuffer())
                saved_filenames.append(file.name)
            data_files[save_folder] = saved_filenames

        submitted = st.form_submit_button("Add Model Task")
        if submitted:
            new_task = Task(new_task_id, task_name, selected_project.id, task_stage,
                            date=dt.datetime.strftime(date, DATE_FORMAT),
                            data_files=data_files,
                            description=description)
            tasks_info.add(new_task)
            tasks_info.save()

            st.markdown("### Task ({}) ({}) added to Project ({})".format(new_task_id, task_name, selected_project.id))


def update_model_task(selected_project):
    selected_task, selected_index = select_task(selected_project.id)
    if not selected_task:
        return

    with st.form("Update a Model Task"):
        task_name = st.text_input("**Task Name:**", selected_task.name)
        description = st.text_area("Description", selected_task.description)
        selected_date = dt.datetime.now()
        if selected_task.date:
            selected_date = dt.datetime.strptime(selected_task.date, DATE_FORMAT)
        date = st.date_input("**Date:**", selected_date)
        default_index = ModelTaskType.get_all_types().index(selected_task.state_name)
        task_stage = st.selectbox("Task type", ModelTaskType.get_all_types(), index=default_index)

        save_folder = os.path.join(ADQ_WORKING_FOLDER, str(selected_project.id), str(selected_task.id))

        uploaded_files = utils.generate_file_tree(save_folder, "*")
        if uploaded_files and len(uploaded_files) > 0:
            with st.expander("{}".format(selected_task.id)):
                for file in uploaded_files[save_folder]:
                    st.markdown("📄{}".format(file))

        new_files = st.file_uploader("Upload artifacts", accept_multiple_files=True)

        if new_files:
            # Save the uploaded file
            for file in new_files:
                with open(os.path.join(save_folder, file.name), "wb") as f:
                    f.write(file.getbuffer())
                uploaded_files[save_folder].append(file.name)

        submitted = st.form_submit_button("Update Model Task")
        if submitted:
            selected_task.name = task_name
            selected_task.description = description
            selected_task.date = dt.datetime.strftime(date, DATE_FORMAT)
            selected_task.state_name = task_stage
            selected_task.data_files = uploaded_files

            tasks_info = TasksInfo.get_tasks_info()
            tasks_info.update_task(selected_task)
            tasks_info.save()

            st.markdown("### Updated Task ({}) ({}) in Project ({})".format(selected_task.id,
                                                                            task_name,
                                                                            selected_project.id))


def update_task():
    selected_project = select_project(is_sidebar=True)
    if selected_project:
        if selected_project.extended_properties:
            update_model_task(selected_project)
        else:
            st.sidebar.write("Update data task is coming soon")


def review_task():
    selected_project = select_project(is_sidebar=True)
    if selected_project:
        if selected_project.extended_properties:
            review_model_task(selected_project)
        else:
            app.main(selected_project)


def review_model_task(selected_project):
    selected_task, selected_index = select_task(selected_project.id)
    if selected_task and selected_task.data_files and len(selected_task.data_files) > 0:
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


def delete_task():
    selected_project = select_project(is_sidebar=True)
    if not selected_project:
        return

    selected_task, selected_index = select_task(selected_project.id)
    if selected_task:
        delete_confirmed = st.sidebar.button("Are you sure you want to delete the task ({}) of project ({}-{})?"
                                             .format(selected_task.id, selected_project.id, selected_project.name))
        if delete_confirmed:
            # projects_info = get_projects_info()
            tasks_info = TasksInfo.get_tasks_info()
            tasks_info.tasks.remove(selected_task)

            task_folder_to_delete = os.path.join(ADQ_WORKING_FOLDER,
                                                 str(selected_project.id),
                                                 str(selected_task.id))
            print("Deleting folder {}".format(task_folder_to_delete))
            if os.path.exists(task_folder_to_delete):
                shutil.rmtree(task_folder_to_delete)
            st.markdown("## Deleted task {} {}".format(selected_task.id, selected_task.name))
            tasks_info.save()


def main():
    menu = {
        "Add Task": lambda: add_task(),
        "Assign Tasks": lambda: assign_tasks(),
        "Update Task": lambda: update_task(),
        "Review Task": lambda: review_task(),
        "Delete Task": lambda: delete_task(),
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
