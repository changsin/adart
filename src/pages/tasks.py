import copy
import importlib.util
import json
import os.path
import random
import shutil

spec = importlib.util.find_spec("src")
if spec is None:
    import sys
    from pathlib import Path

    path_root = Path(__file__).parents[2]
    sys.path.append(str(path_root))

from src.common.constants import (
    ADQ_WORKING_FOLDER,
    ModelTaskType
)
from src.common.charts import *
from src.home import (
    get_tasks_info,
    select_project,
    select_task
)
from src.pages import metrics
from src.models.projects_info import Project
from src.models.tasks_info import Task, TaskState
from src.common import utils
import src.viewer.app as app



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
        utils.to_file(json.dumps(sampled_dart_labels, default=utils.default, indent=2), task_folder, label_filename)

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


def create_tasks():
    selected_project = select_project(is_sidebar=True)
    if selected_project:
        dart_labels_dict = metrics.load_label_files(selected_project.label_files)
        images_per_label_file_dict = dict()
        if dart_labels_dict.items() is not None:
            for labels_file, dart_labels in dart_labels_dict.items():
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

                    sample_data(selected_project, dart_labels_dict, df_sample_count)


def update_task():
    st.sidebar.write("Coming soon")


def add_task():
    selected_project = select_project(is_sidebar=True)
    if selected_project:
        if selected_project.extended_properties:
            add_model_task(selected_project)
        else:
            st.sidebar.write("Add data task is coming soon")


def add_model_task(selected_project: Project):
    with st.form("Create a Model Project"):
        task_name = st.text_input("**Task Name:**")
        date = st.date_input("**Date:**")
        task_stage = st.selectbox("Task type", ModelTaskType.get_all_types())

        uploaded_files = st.file_uploader("Upload artifacts", accept_multiple_files=True)

        tasks_info = get_tasks_info()
        new_task_id = tasks_info.get_next_task_id()

        save_folder = os.path.join(ADQ_WORKING_FOLDER, str(selected_project.id), str(new_task_id))
        if not os.path.exists(save_folder):
            os.mkdir(save_folder)

        if uploaded_files:
            # Save the uploaded file
            for file in uploaded_files:
                with open(os.path.join(save_folder, file.name), "wb") as f:
                    f.write(file.getbuffer())

        submitted = st.form_submit_button("Add Model Task")
        if submitted:
            new_task = Task(new_task_id, task_name, selected_project.id, task_stage, date=date)
            tasks_info = get_tasks_info()
            tasks_info.add(new_task)
            tasks_info.save()

            st.markdown("## Task ({}) ({}) added to Project ({})".format(new_task_id, task_name, selected_project.id))


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
            tasks_info = get_tasks_info()
            tasks_info.tasks.remove(selected_task)

            task_folder_to_delete = os.path.join(ADQ_WORKING_FOLDER,
                                                 str(selected_project.id),
                                                 str(selected_index))
            if os.path.exists(task_folder_to_delete):
                shutil.rmtree(task_folder_to_delete)
            st.markdown("## Deleted task {} {}".format(selected_task.id, selected_task.name))
            tasks_info.save()


def main():
    menu = {
        "Create Tasks": lambda: create_tasks(),
        "Review Task": lambda: app.main(),
        "Update Task": lambda: update_task(),
        "Add Task": lambda: add_task(),
        "Delete Task": lambda: delete_task(),
    }

    # Create a sidebar with menu options
    selected_action = st.sidebar.radio("Choose action", list(menu.keys()))

    if selected_action:
        # Call the selected method based on the user's selection
        menu[selected_action]()


if __name__ == '__main__':
    main()
