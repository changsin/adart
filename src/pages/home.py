import os.path
from PIL import Image
import pandas as pd
import streamlit as st

import src.api.api_base
import src.common.utils as utils
from src.api.api_base import ApiBase
from src.api.api_local import ApiLocal
from src.api.api_remote import ApiRemote
from src.common.constants import (
    ADQ_WORKING_FOLDER,
    PROJECTS,
    SUPPORTED_IMAGE_FILE_EXTENSIONS
)
from src.models.projects_info import ProjectsInfo, Project
from src.models.tasks_info import Task, TasksInfo
from src.common.logger import get_logger

LOCALHOST = "http://localhost"

logger = get_logger(__name__)


def api_target() -> ApiBase:
    token = st.session_state['token']
    url_base = st.session_state['url_base']
    if url_base == LOCALHOST:
        return ApiLocal(url_base, token)
    else:
        return ApiRemote(url_base, token)


def get_projects_info():
    return ProjectsInfo.from_json(api_target().list_projects())


def get_tasks_info():
    return TasksInfo.from_json(api_target().list_tasks())


def select_project(is_sidebar=True):
    projects_info = get_projects_info()
    if projects_info.num_count > 0:
        df_projects = pd.DataFrame(projects_info.to_json()[PROJECTS])
        df_project_id_names = df_projects[["id", "name"]]
        options = ["{}-{}".format(project_id, name)
                   for project_id, name in df_project_id_names[["id", "name"]].values.tolist()]
        # set an empty string as the default selection - no action
        options.append("")
        if is_sidebar:
            selected_project = st.sidebar.selectbox("Select project",
                                                    options=options,
                                                    index=len(options) - 1)

        else:
            selected_project = st.selectbox("Select project",
                                            options=options,
                                            index=len(options) - 1)
        if selected_project:
            project_id, name, = selected_project.split('-', maxsplit=1)
            return projects_info.get_project_by_id(int(project_id))
    else:
        st.markdown("**No project is created!**")


def select_task(project_id: int, label="Select task") -> Task:
    tasks_info = get_tasks_info()
    tasks = tasks_info.get_tasks_by_project_id(project_id)
    if tasks and len(tasks) > 0:
        df_tasks = pd.DataFrame([task.to_json() for task in tasks])
        df_tasks = df_tasks[["id", "name", "project_id"]]
        df_filtered = df_tasks[df_tasks['project_id'] == project_id]
        options = ["{}-{}".format(task_id, name)
                   for task_id, name, project_id in
                   df_filtered[["id", "name", "project_id"]].values.tolist()]
        # set an empty string as the default selection - no action
        options.append("")
        selected_task = st.sidebar.selectbox(label,
                                             options=options,
                                             index=len(options) - 1)
        if selected_task:
            task_id, _ = selected_task.split('-', maxsplit=1)
            return tasks_info.get_task_by_id(int(task_id))
    else:
        st.markdown("**No task is created!**")


def generate_thumbnails(folder_path, thumbnail_size=(128, 128), output_folder="thumbnails"):
    os.makedirs(output_folder, exist_ok=True)

    thumbnail_filenames = []

    for filename in os.listdir(folder_path):
        if any(filename.endswith(ext) for ext in SUPPORTED_IMAGE_FILE_EXTENSIONS):
            image_path = os.path.join(folder_path, filename)
            output_path = os.path.join(output_folder, filename)

            try:
                with Image.open(image_path) as image:
                    image.thumbnail(thumbnail_size)
                    image.save(output_path)
                    thumbnail_filenames.append(output_path)
            except Exception as e:
                logger.error(f"Error processing {filename}: {str(e)}")

    return thumbnail_filenames


def get_data_files(folder, is_thumbnails=False):
    """
    returns a diction of data_filenames or thumbnails
    :param folder: folder name
    :param is_thumbnails: returns thumbnails if true
    :return: data_files by default; returns thumbnails if true
    """
    data_files = dict()
    data_folder = os.path.join(folder, "data")
    thumbnails_folder = os.path.join(folder, "thumbnails")

    if is_thumbnails:
        if not os.path.exists(thumbnails_folder):
            generate_thumbnails(data_folder, output_folder=thumbnails_folder)

        data_folder = thumbnails_folder

    data_filenames = utils.glob_files(data_folder,
                                      SUPPORTED_IMAGE_FILE_EXTENSIONS)
    data_filenames.sort()
    data_files["."] = data_filenames

    return data_files


def get_label_files(selected_project: Project):
    label_files = dict()
    tasks_info = get_tasks_info()
    tasks = tasks_info.get_tasks_by_project_id(selected_project.id)
    if tasks and len(tasks) > 0:
        anno_files = []
        project_folder = os.path.join(ADQ_WORKING_FOLDER, str(selected_project.id))
        for task in tasks:
            if task.anno_file_name:
                anno_files.append(os.path.basename(task.anno_file_name))

        label_files[project_folder] = anno_files
    return label_files


def get_token(url, username: str, password: str):
    if "http://localhost" == url and username == 'admin' and password == "password1234!":
        return "token"
    else:
        token = src.api.api_base.get_access_token(url + "/api/v1/login/access-token", username, password)
        print("access token is {}".format(token))
        return token


def login():
    selected_url = st.selectbox("Select server", [
        LOCALHOST,
        "http://192.168.12.54",
    ])

    col1, col2 = st.columns(2)
    col1.title("ADaRT Service")
    col1.write('Brought to you by TW')
    username = col2.text_input('User', key='user', value="")
    password = col2.text_input('Password', type="password", value="")

    login_button = col2.button("Login")
    if login_button:
        token = get_token(selected_url, username, password)

        if username and password and not token:
            col2.warning("Please check your credentials")
            return False
        else:
            st.session_state['token'] = token
            st.session_state['url_base'] = selected_url
            return True


def logout():
    button_label = st.empty()
    # button_label.text = "Log out"
    logout_clicked = st.sidebar.button("Logout")
    if logout_clicked:
        button_label.text = "Logged out"
        st.session_state['token'] = None
        st.session_state['projects'] = None


def is_authenticated():
    return st.session_state.get('token')


def main():
    st.header("**Adart** - AI Data Reviewing Tool")

    resources_dir = "resources"
    intro_markdown = utils.from_text_file(os.path.join(resources_dir, 'adart_homepage.md'))
    st.markdown(intro_markdown, unsafe_allow_html=True)

    image_path = os.path.join(resources_dir, 'workflow1.png')
    st.image(image_path, use_column_width=False)


if __name__ == '__main__':
    if not is_authenticated():
        login()
    else:
        main()
        
        logout()
