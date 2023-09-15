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
    CVAT_BOX_XML,
    HUMANF_SEG_JSON,
    GPR_JSON,
    STRADVISION_XML,
    LABEL_ON_JSON,
    SUPPORTED_IMAGE_FILE_EXTENSIONS,
    SUPPORTED_LABEL_FILE_EXTENSIONS,
    SUPPORTED_LABEL_FORMATS,
    YOLO_V5_TXT)
from src.common.convert_lib import (
    from_gpr_json,
    from_yolo_txt)
from src.common.logger import get_logger
from src.converters.cvat_reader import CVATReader
from src.converters.cvat_writer import CVATWriter
from src.converters.humanf_seg_reader import HumanFReader
from src.converters.labelon_reader import LabelOnReader
from src.converters.project85_writer import Project85Writer
from src.converters.stvision_reader import StVisionReader
from src.models.adq_labels import AdqLabels
from src.models.data_labels import DataLabels
from src.models.projects_info import Project
from src.models.tasks_info import Task, TaskState
from src.pages.users import select_user
from .home import (
    api_target,
    get_tasks_info,
    get_task_pointers,
    is_authenticated,
    login,
    logout,
    select_project,
    select_task)

logger = get_logger(__name__)

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


def sample_data(selected_project: Project, data_labels_dict: dict, df_sample_count: pd.DataFrame):
    data_total_count, data_sample_count = 0, 0

    sampled = {}
    for index, row in df_sample_count.iterrows():
        label_filename = row['filename']
        sample_count = row['count']

        dart_labels = data_labels_dict[label_filename]
        sampled_data_labels = copy.deepcopy(dart_labels)
        random.shuffle(sampled_data_labels.images)

        sampled_data_labels.images = sampled_data_labels.images[:sample_count]
        sampled[label_filename] = sampled_data_labels

        # save the sample label file
        task_folder = os.path.join(ADQ_WORKING_FOLDER, str(selected_project.id), str(index))
        if not os.path.exists(task_folder):
            os.mkdir(task_folder)
        utils.to_file(json.dumps(sampled_data_labels, default=utils.default, indent=2),
                      os.path.join(task_folder, label_filename))

        tasks_info = get_tasks_info()
        task_name = "{}-{}".format(selected_project.id, label_filename)
        object_count = sum(image.objects for image in sampled_data_labels.images)
        new_task = Task(task_name,
                        project_id=selected_project.id,
                        state_id=TaskState.DVS_NEW.value,
                        state_name=str(TaskState.DVS_NEW.description),
                        anno_file_name=label_filename,
                        data_count=len(sampled_data_labels.images),
                        object_count=object_count
                        )
        tasks_info.add(new_task)
        tasks_info.save()

        data_total_count += len(dart_labels.images)
        data_sample_count += len(sampled_data_labels.images)

    selected_project.data_total_count = data_total_count
    selected_project.data_sample_count = data_sample_count
    api_target().update_project(selected_project.to_json())

    return sampled


def _convert_anno_files(labels_format_type, save_file_stem, saved_data_filenames, saved_anno_filenames):
    converted_anno_files = []
    save_folder = os.path.dirname(save_file_stem)
    if labels_format_type == CVAT_BOX_XML:
        for idx, anno_file in enumerate(saved_anno_filenames):
            converted_filename = f"{save_file_stem}-{idx}.json"

            reader = CVATReader()
            logger.info(f"parsing {anno_file}")
            parsed_dict = reader.parse([anno_file], saved_data_filenames)
            data_labels = DataLabels.from_adq_labels(AdqLabels.from_json(parsed_dict))
            data_labels.save(converted_filename)
            converted_anno_files.append(converted_filename)
    elif labels_format_type == HUMANF_SEG_JSON:
        for idx, anno_file in enumerate(saved_anno_filenames):
            converted_filename = f"{save_file_stem}-{idx}.json"

            reader = HumanFReader()
            logger.info(f"parsing {anno_file}")
            parsed_dict = reader.parse([anno_file], saved_data_filenames)
            data_labels = DataLabels.from_json(parsed_dict)
            data_labels.save(converted_filename)
            converted_anno_files.append(converted_filename)
    else:
        converted_filename = f"{save_file_stem}.json"
        if labels_format_type == STRADVISION_XML:
            reader = StVisionReader()
            parsed_dict = reader.parse(saved_anno_filenames, saved_data_filenames)
            data_labels = DataLabels.from_json(parsed_dict)
            data_labels.save(converted_filename)
        elif labels_format_type == GPR_JSON:
            converted_filename = from_gpr_json("11", saved_anno_filenames, save_folder)
        elif labels_format_type == YOLO_V5_TXT:
            converted_filename = from_yolo_txt("11", saved_anno_filenames, saved_data_filenames, save_folder)
        elif labels_format_type == LABEL_ON_JSON:
            reader = LabelOnReader()
            parsed_dict = reader.parse(saved_anno_filenames, saved_data_filenames)
            data_labels = DataLabels.from_json(parsed_dict)
            data_labels.save(converted_filename)

        converted_anno_files.append(converted_filename)

    return converted_anno_files


def change_status():
    selected_project = select_project()
    if selected_project:
        with st.form("Add Data Task"):
            st.subheader(f"Assign tasks to users for project {selected_project.name}")
            task_pointers = get_task_pointers(selected_project.id)
            task_pointers_checked = []
            if len(task_pointers.task_pointers) > 0:
                for task_pointer in task_pointers.task_pointers:
                    if st.checkbox(task_pointer.name):
                        task_pointers_checked.append(task_pointer)
            else:
                st.write("No task is created")

            selected_state = st.radio("State", TaskState.get_all_types())

            assigned = st.form_submit_button("Assign tasks")
            if assigned:
                for task_pointer in task_pointers_checked:
                    task = task_pointers.get_task_by_id(task_pointer.id)
                    task.state_name = selected_state
                    task.state_id = TaskState.get_enum_value(selected_state)

                    task.save()

                st.write(f"Changed {[task_ptr.name for task_ptr in task_pointers_checked]} to {selected_state}")


def assign_tasks():
    selected_project = select_project()
    if selected_project:
        with st.form("Change Data Task"):
            st.subheader(f"Assign tasks to users for project {selected_project.name}")
            # get all task pointers
            task_pointers = get_task_pointers()
            project_task_pointers = list(filter(
                lambda x: x.project_id == selected_project.id, task_pointers.task_pointers))
            task_pointers_checked = []
            if len(project_task_pointers) > 0:
                for idx, task_pointer in enumerate(project_task_pointers):
                    if st.checkbox(task_pointer.name, key=idx):
                        task_pointers_checked.append(task_pointer)
            else:
                st.write("No task is created")

            selected_user = select_user(is_sidebar=False)
            if selected_user:
                st.write(f"User {selected_user.full_name} is selected")

            assigned = st.form_submit_button("Assign tasks")
            if assigned:
                for task_pointer in task_pointers_checked:
                    task = task_pointers.get_task_by_id(task_pointer.id)
                    task.reviewer_fullname = selected_user.full_name
                    task.reviewer_id = selected_user.id
                    task.state_name = TaskState.DVS_WORKING.description
                    task.state_id = TaskState.DVS_WORKING._value_

                    task.save()
                    task_pointers.update_task(task)

                task_pointers.save()
                st.write(f"Assigned {[task.name for task in task_pointers_checked]} to {selected_user.full_name}")


def add_tasks():
    selected_project = select_project()
    if selected_project:
        add_data_tasks(selected_project)


def _save_uploaded_files(uploaded_files, sub_folders_str: str):
    to_save_folder = ADQ_WORKING_FOLDER

    sub_folders = sub_folders_str.split("/")
    for sub_folder in sub_folders:
        to_save_folder = os.path.join(to_save_folder, sub_folder)
        if not os.path.exists(to_save_folder):
            os.mkdir(to_save_folder)

    saved_filenames = []
    for file in uploaded_files:
        with open(os.path.join(to_save_folder, file.name), "wb") as f:
            f.write(file.getbuffer())
        saved_filenames.append(os.path.join(to_save_folder, file.name))
    saved_filenames.sort()

    return saved_filenames


def add_data_tasks(selected_project: Project):
    with st.form("Add Data Task"):
        task_name = st.text_input("**Task Name:**")

        # Users can upload either image files only or label files only
        selected_file_types = st.selectbox("**Image file types**", [SUPPORTED_IMAGE_FILE_EXTENSIONS],
                                           index=len([SUPPORTED_IMAGE_FILE_EXTENSIONS]) - 1)
        uploaded_data_files = st.file_uploader("Upload data files", selected_file_types, accept_multiple_files=True)
        uploaded_label_files = st.file_uploader("Upload label files", SUPPORTED_LABEL_FILE_EXTENSIONS,
                                                accept_multiple_files=True)
        labels_format_type = st.selectbox("**Choose format:**", SUPPORTED_LABEL_FORMATS)

        saved_data_filenames = None

        if uploaded_data_files:
            saved_data_filenames = _save_uploaded_files(uploaded_data_files,
                                                        f"{selected_project.id}/data")

        if uploaded_label_files:
            saved_anno_filenames = _save_uploaded_files(uploaded_label_files,
                                                        f"{selected_project.id}/labels")

        submitted = st.form_submit_button("Add Data Tasks")
        if submitted:
            data_total_count = 0
            if not uploaded_data_files and not uploaded_label_files:
                st.warning("Please upload files")
                return

            project_folder = os.path.join(ADQ_WORKING_FOLDER, str(selected_project.id))
            convert_file_stem = os.path.join(project_folder, "anno")
            converted_anno_filenames = []

            if uploaded_label_files:
                converted_anno_filenames = _convert_anno_files(labels_format_type,
                                                               convert_file_stem,
                                                               saved_data_filenames,
                                                               saved_anno_filenames)
            else:
                # if no label files are uploaded, create an empty label file
                anno_filename = f"{convert_file_stem}.json"
                data_labels_file = DataLabels.from_image_filenames(saved_data_filenames)
                data_labels_file.save(anno_filename)
                converted_anno_filenames.append(anno_filename)

            # now create tasks
            for idx, converted_anno_filename in enumerate(converted_anno_filenames):
                data_labels = DataLabels.load(converted_anno_filename)
                data_count = len(data_labels.images)
                object_count = sum(len(image.objects) for image in data_labels.images)

                next_task_id = api_target().get_next_task_id()
                task_folder = os.path.join(project_folder, f"{next_task_id}")
                moved_converted_anno_filename = os.path.join(task_folder,
                                                        os.path.basename(converted_anno_filename))
                if not os.path.exists(os.path.dirname(moved_converted_anno_filename)):
                    os.mkdir(os.path.dirname(moved_converted_anno_filename))
                    os.mkdir(os.path.join(task_folder, "data"))

                shutil.move(converted_anno_filename, moved_converted_anno_filename)

                for image in data_labels.images:
                    cur_data_filename = os.path.join(project_folder, "data", image.name)
                    target_filename = os.path.join(task_folder, "data", image.name)
                    if not os.path.exists(cur_data_filename):
                        base_name = os.path.basename(cur_data_filename)
                        # this hack is for project85
                        real_name = str(base_name).replace(task_name, "")
                        cur_data_filename = os.path.join(project_folder, "data", real_name)

                    if os.path.exists(cur_data_filename):
                        shutil.move(cur_data_filename, target_filename)

                new_task = Task(name=f"{task_name}-{idx}",
                                project_id=selected_project.id,
                                dir_name=project_folder,
                                anno_file_name=moved_converted_anno_filename,
                                state_id=TaskState.DVS_NEW.value,
                                state_name=TaskState.DVS_NEW.description,
                                data_count=data_count,
                                object_count=object_count)
                data_total_count += data_count
                response = api_target().create_task(new_task.to_json())
                logger.info(response)
                st.write(f"Task {response['id']} {response['name']} created")

            selected_project.task_total_count += len(converted_anno_filenames)
            selected_project.data_total_count += data_total_count
            api_target().update_project(selected_project.to_json())


def delete_task():
    selected_project = select_project(is_sidebar=True)
    if not selected_project:
        return

    selected_task = select_task(selected_project.id)
    if selected_task:
        delete_confirmed = st.sidebar.button("Are you sure you want to delete the task ({}) of project ({}-{})?"
                                             .format(selected_task.id, selected_project.id, selected_project.name))
        if delete_confirmed:
            api_target().delete_task(selected_task.id)

            st.markdown("## Deleted task {} {}".format(selected_task.id, selected_task.name))


def convert_task():
    selected_project = select_project(is_sidebar=True)
    if not selected_project:
        return

    selected_task = select_task(selected_project.id)
    if selected_task:

        with st.form("Convert"):
            saved_cuboid_filenames = []
            uploaded_cuboid_files = st.file_uploader("Upload cuboid files",
                                                     SUPPORTED_LABEL_FILE_EXTENSIONS,
                                                     accept_multiple_files=True)

            if uploaded_cuboid_files:
                saved_cuboid_filenames = _save_uploaded_files(uploaded_cuboid_files,
                                                              f"{selected_project.id}/{selected_task.id}/cuboid")

            options = ["Project85", "CVAT XML"]
            selected_format = st.selectbox("**Convert to**",
                                           options,
                                           index=len(options) - 1)
            convert_confirmed = st.form_submit_button("Convert the task ({}) of project ({}-{})?"
                                         .format(selected_task.id, selected_project.id, selected_project.name))
            if convert_confirmed:
                if selected_format == "Project85":
                    project_folder = os.path.join(ADQ_WORKING_FOLDER, str(selected_project.id))
                    to_save_folder = os.path.join(project_folder, str(selected_task.id) + "_converted")
                    if not os.path.exists(to_save_folder):
                        os.mkdir(to_save_folder)

                    writer = Project85Writer()
                    converted_filename = os.path.join(to_save_folder, f"converted-{selected_task.id}.json")
                    writer.write(selected_task.anno_file_name, converted_filename)

                    st.markdown("## Converted task {} {}".format(selected_task.id, selected_task.name))
                elif selected_format == "CVAT XML":
                    project_folder = os.path.join(ADQ_WORKING_FOLDER, str(selected_project.id))
                    to_save_folder = os.path.join(project_folder, str(selected_task.id) + "_converted")
                    if not os.path.exists(to_save_folder):
                        os.mkdir(to_save_folder)

                    writer = CVATWriter()
                    converted_filename = os.path.join(to_save_folder, f"converted-{selected_task.id}.xml")
                    writer.write(selected_task.anno_file_name, converted_filename)

                    st.markdown("## Converted task {} {}".format(selected_task.id, selected_task.name))


def main():
    # Clear the sidebar
    st.sidebar.empty()
    # Clear the main page
    st.empty()

    menu = {
        # "Sample Tasks": lambda: create_data_tasks(),
        "Add Tasks": lambda: add_tasks(),
        "Assign Tasks": lambda: assign_tasks(),
        "Change Status": lambda: change_status(),
        "Delete Task": lambda: delete_task(),
        "Convert Task": lambda: convert_task(),
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
