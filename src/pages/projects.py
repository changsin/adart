import os
import shutil

import streamlit as st

from src.common.constants import (
    ADQ_WORKING_FOLDER,
)
from src.models.projects_info import Project, ModelProject
from .home import (
    api_target,
    get_projects_info,
    get_project_pointers,
    get_tasks_info,
    is_authenticated,
    login,
    logout,
    select_project)

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
            st.markdown(f"**Data folder:** {save_folder}")

            new_project_dict = Project(name,
                                       dir_name=save_folder,
                                       description=description
                                       ).to_json()
            response = api_target().create_project(new_project_dict)
            st.dataframe(response)
            st.write("Project {} created".format(name))


def update_project():
    selected_project = select_project(is_sidebar=True)
    if selected_project:
        update_data_project(selected_project)


def update_data_project(selected_project: Project):
    st.sidebar.write("Coming soon")


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
            tasks_info = get_tasks_info()
            for selected_task in tasks_info.tasks:
                if selected_task.project_id == selected_project.id:
                    tasks_info.tasks.remove(selected_task)
            tasks_info.save()

            # Finally delete the project itself
            projects_info = get_projects_info()
            projects_info.projects.remove(selected_project)

            st.markdown("## Deleted project {} {}".format(selected_project.id, selected_project.name))
            projects_info.save()


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
