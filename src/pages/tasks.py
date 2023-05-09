import copy
import datetime as dt
import json
import os.path
import random
import shutil

import pandas as pd
import streamlit as st

from src.common import utils
from src.common.constants import (
    ADQ_WORKING_FOLDER,
    CVAT_XML,
    GPR_JSON,
    ModelTaskType,
    STRADVISION_XML,
    SUPPORTED_IMAGE_FILE_EXTENSIONS,
    SUPPORTED_LABEL_FILE_EXTENSIONS,
    SUPPORTED_LABEL_FORMATS,
    YOLO_V5_TXT)
from src.common.convert_lib import (
    from_gpr_json,
    from_yolo_txt)
from src.converters.cvat_reader import CVATReader
from src.converters.stvision_reader import StVisionReader
from src.models.adq_labels import AdqLabels
from src.models.data_labels import DataLabels
from src.models.projects_info import Project
from src.models.tasks_info import Task, TaskState
from src.pages.users import select_user
from .home import (
    api_target,
    get_tasks_info,
    is_authenticated,
    login,
    logout,
    select_project,
    select_task)

DATE_FORMAT = "%Y %B %d %A"


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


def _calculate_sample_count(count, percent):
    return int((count * percent) / 100)


def _calculate_sample_distribution(df_total_count: pd.DataFrame,
                                   sample_percent: int) -> pd.DataFrame:
    df_sample_count = df_total_count.copy()

    for index, row in df_total_count.iterrows():
        sample_count = _calculate_sample_count(row['count'], sample_percent)
        if sample_count < 1.0:
            st.warning("Please set a higher percentage to pick at least one file per folder")
            return None
        else:
            df_sample_count.iloc[index] = (row['filename'], sample_count)

    return df_sample_count


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

        tasks_info = get_tasks_info()
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


def create_data_tasks():
    selected_project = select_project()
    if selected_project:
        if not selected_project.label_files:
            st.write("No data to sample. Please add data or add tasks instead")
        else:
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
                        st.write("Sampling ")
                        total_count = df_total_count['count'].sum()
                        total_sample_count = _calculate_sample_count(total_count, sample_percent)

                        if is_keep_folders:
                            df_sample_count = _calculate_sample_distribution(df_total_count, sample_percent)
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
        with st.form("Add Data Task"):
            st.subheader(f"Assign tasks to users for project {selected_project.name}")
            tasks_info = get_tasks_info()
            tasks = tasks_info.get_tasks_by_project_id(selected_project.id)
            if tasks and len(tasks) > 0:
                for task in tasks:
                    if st.checkbox(task.name):
                        # Do something when the checkbox is selected
                        st.write(f"Task {task.name} is checked")
            else:
                st.write("No task is created")

            selected_user = select_user(is_sidebar=False)
            if selected_user:
                st.write(f"User {selected_user} is picked")

            assigned = st.form_submit_button("Assign tasks")
            if assigned:
                st.write(f"Assigned {tasks} to {selected_user}")
                # TODO: update the status in tasks and projects
                for task in tasks:
                    task.reviewer_fullname = selected_user.full_name
                    task.reviewer_id = selected_user.id
                    task.state_name = TaskState.DVS_WORKING.description
                    task.state_id = TaskState.DVS_WORKING._value_
                tasks_info.save()


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
                                                SUPPORTED_LABEL_FILE_EXTENSIONS,
                                                accept_multiple_files=True)

        tasks_info = get_tasks_info()
        new_task_id = tasks_info.get_next_task_id()

        save_folder = os.path.join(ADQ_WORKING_FOLDER, str(selected_project.id), str(new_task_id))
        if not os.path.exists(save_folder):
            os.mkdir(save_folder)

        data_files = dict()
        if uploaded_data_files:
            # Save the uploaded files
            saved_data_filenames = []
            for file in uploaded_data_files:
                with open(os.path.join(save_folder, file.name), "wb") as f:
                    f.write(file.getbuffer())
                saved_data_filenames.append(file.name)
            data_files[save_folder] = saved_data_filenames
            saved_data_filenames.sort()

        labels_format_type = st.selectbox("**Choose format:**", SUPPORTED_LABEL_FORMATS)
        if uploaded_label_files:
            # Save the uploaded files in origin folder
            ori_folder = os.path.join(save_folder, "origin")
            if not os.path.exists(ori_folder):
                os.mkdir(ori_folder)

            saved_anno_filenames = []
            for file in uploaded_label_files:
                with open(os.path.join(ori_folder, file.name), "wb") as f:
                    f.write(file.getbuffer())
                saved_anno_filenames.append(os.path.join(ori_folder, file.name))

            saved_anno_filenames.sort()
            converted_filename = os.path.join(save_folder, "converted.json")

            if labels_format_type == STRADVISION_XML:
                reader = StVisionReader()
                parsed_dict = reader.parse(saved_anno_filenames, saved_data_filenames)
                data_labels = DataLabels.from_json(parsed_dict)
                data_labels.save(converted_filename)
            elif labels_format_type == CVAT_XML:
                reader = CVATReader()
                parsed_dict = reader.parse(saved_anno_filenames, saved_data_filenames)
                data_labels = DataLabels.from_adq_labels(AdqLabels.from_json(parsed_dict))
                data_labels.save(converted_filename)
            elif labels_format_type == GPR_JSON:
                converted_filename = from_gpr_json("11", saved_anno_filenames, save_folder)
            elif labels_format_type == YOLO_V5_TXT:
                converted_filename = from_yolo_txt("11", saved_anno_filenames, saved_data_filenames, save_folder)

        # label_files[save_folder] = [converted_filename]
        submitted = st.form_submit_button("Add Data Task")
        if submitted:
            data_count = len(saved_data_filenames)
            new_task = Task(new_task_id, task_name, selected_project.id, "New",
                            date=str(dt.datetime.now()),
                            count=data_count,
                            anno_file_name=converted_filename)
            tasks_info.add(new_task)
            tasks_info.save()

            selected_project.task_total_count += data_count
            api_target().update_project(selected_project.to_json())

            st.markdown("### Task ({}) ({}) added to Project ({})".format(new_task_id, task_name, selected_project.id))


def add_model_task(selected_project: Project):
    with st.form("Add a Model Task"):
        task_name = st.text_input("**Task Name:**")
        description = st.text_area("Description")
        date = st.date_input("**Date:**")
        task_stage = st.selectbox("Task type", ModelTaskType.get_all_types())

        uploaded_files = st.file_uploader("Upload artifacts", accept_multiple_files=True)

        tasks_info = get_tasks_info()
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
    selected_task = select_task(selected_project.id)
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

            tasks_info = get_tasks_info()
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


def delete_task():
    selected_project = select_project(is_sidebar=True)
    if not selected_project:
        return

    selected_task = select_task(selected_project.id)
    if selected_task:
        delete_confirmed = st.sidebar.button("Are you sure you want to delete the task ({}) of project ({}-{})?"
                                             .format(selected_task.id, selected_project.id, selected_project.name))
        if delete_confirmed:
            tasks_info = get_tasks_info()
            tasks_info.remove(selected_task)

            task_folder_to_delete = os.path.join(ADQ_WORKING_FOLDER,
                                                 str(selected_project.id),
                                                 str(selected_task.id))
            if os.path.exists(task_folder_to_delete):
                shutil.rmtree(task_folder_to_delete)
            tasks_info.save()
            st.markdown("## Deleted task {} {}".format(selected_task.id, selected_task.name))


def main():
    # Clear the sidebar
    st.sidebar.empty()
    # Clear the main page
    st.empty()

    menu = {
        "Sample Tasks": lambda: create_data_tasks(),
        "Add Task": lambda: add_task(),
        "Assign Tasks": lambda: assign_tasks(),
        "Update Task": lambda: update_task(),
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
