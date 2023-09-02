import os
import shutil

import streamlit as st
from src.common.logger import get_logger

from src.common.constants import (
    ADQ_WORKING_FOLDER,
)
from src.models.projects_info import Project
from .home import (
    api_target,
    get_project_pointers,
    get_task_pointers,
    is_authenticated,
    login,
    logout,
    select_project)

logger = get_logger(__name__)

MULTI_SELECT_SEP = ';'


def create_project():
    menu = {
        "data": lambda: create_data_project()
    }

    # Create a sidebar with menu options
    selected_project_type = st.sidebar.selectbox("Project type", list(menu.keys()))
    if selected_project_type:
        # Call the selected method based on the user's selection
        menu[selected_project_type]()


def create_data_project():
    with st.form("Create a Data Project"):
        name = st.text_input("**Name:**")
        description = st.text_area("Description")
        projects_pointers = get_project_pointers()
        dir_name = projects_pointers.get_next_project_id()
        save_folder = os.path.join(ADQ_WORKING_FOLDER, str(dir_name))
        if not os.path.exists(save_folder):
            os.mkdir(save_folder)

        submitted = st.form_submit_button("Create project")
        if submitted:
            st.markdown(f"**Name:** {name}")
            new_project_dict = Project(name,
                                       dir_name=save_folder,
                                       description=description
                                       ).to_json()
            response = api_target().create_project(new_project_dict)
            st.write("Project {} created".format(name))


def update_project():
    selected_project = select_project(is_sidebar=True)
    if selected_project:
        update_data_project(selected_project)


def update_data_project(selected_project: Project):
    with st.form("Update Project"):
        name = st.text_input("**Name:**", value=selected_project.name)
        description = st.text_area("Description", value=selected_project.description)
        submitted = st.form_submit_button("Update project")
        if submitted:
            st.markdown(f"**Name:** {name}")
            selected_project.name = name
            selected_project.description = description
            response = api_target().update_project(selected_project.to_json())
            st.write("Project {} updated".format(name))


def delete_project():
    selected_project = select_project(is_sidebar=True)
    if selected_project:
        delete_confirmed = st.sidebar.button("Are you sure you want to delete the project {}-{}?"
                                             .format(selected_project.id, selected_project.name))
        if delete_confirmed:
            # Delete the artifacts first
            folder_path = os.path.join(ADQ_WORKING_FOLDER, str(selected_project.id))
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)

            # Then all the tasks
            task_pointers = get_task_pointers()
            logger.info(task_pointers.task_pointers)
            for idx, task_pointer in enumerate(task_pointers.task_pointers):
                logger.info(f"Checking {idx} {task_pointer}")
                if task_pointer.project_id == selected_project.id:
                    logger.info(f"Removing {task_pointer}")
                    task_pointers.task_pointers.remove(task_pointer)
                    logger.info(f"Removed {task_pointer}")
                    st.info(f"Removed {task_pointer}")
            task_pointers.save()

            # Finally delete the project itself
            project_pointers = get_project_pointers()
            for project_pointer in project_pointers.project_pointers:
                if project_pointer.id == selected_project.id:
                    project_pointers.project_pointers.remove(project_pointer)
                    break

            project_pointers.save()

            st.markdown("## Deleted project {} {}".format(selected_project.id, selected_project.name))


def main():
    # Clear the sidebar
    st.sidebar.empty()
    # Clear the main page
    st.empty()

    menu = {
        "Create Project": lambda: create_project(),
        "Update Project": lambda: update_project(),
        "Delete Project": lambda: delete_project(),
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
