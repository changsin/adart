import pandas as pd
import streamlit as st
from st_aggrid import AgGrid

from .home import (
    get_projects_info,
    is_authenticated,
    login,
    logout,
    select_project)
from src.common import constants
from src.models.tasks_info import TasksInfo


def view_project():
    selected_project = select_project(is_sidebar=True)

    if selected_project:
        st.markdown("# Project")
        st.dataframe(pd.DataFrame(selected_project.to_json(), index=[0]))

        extended_props = selected_project.extended_properties
        if extended_props:
            st.markdown("## Model validation information")
            st.dataframe(pd.DataFrame.from_dict(extended_props,
                                                orient='index'))

        st.markdown("# Tasks")
        tasks_info = TasksInfo.get_tasks_info()
        tasks = tasks_info.get_tasks_by_project_id(selected_project.id)
        tasks_json = [task.to_json() for task in tasks]
        st.dataframe(pd.DataFrame(tasks_json))


# def model_validation_dashboard():
#     projects_info = get_projects_info()
#     model_projects = []
#     for project in projects_info.projects:
#         if project.extended_properties:
#             model_projects.append(project)
#
#     for model_project in model_projects:
#         model_tasks = get_tasks(model_project.id)
#
#         for model_task in model_tasks:
#             model_task.


def dashboard():
    st.subheader("**Projects**")
    df_projects = pd.DataFrame(columns=constants.PROJECT_COLUMNS)

    projects_info = get_projects_info()
    if projects_info.num_count > 0:
        # turn a class object to json dictionary to be processed by pandas dataframe
        df_projects = pd.DataFrame(projects_info.to_json()[constants.PROJECTS])
        df_projects = df_projects[constants.PROJECT_COLUMNS]

    AgGrid(df_projects)

    st.subheader("**Tasks**")
    tasks_info = TasksInfo.get_tasks_info()
    if len(tasks_info.tasks) > 0:
        df_tasks = pd.DataFrame([task.to_json() for task in tasks_info.tasks])
        df_tasks = df_tasks.rename(columns=lambda x: x.strip() if isinstance(x, str) else x)

        AgGrid(df_tasks)


def main():
    # Clear the sidebar
    st.sidebar.empty()
    # Clear the main page
    st.empty()

    st.markdown("# Dashboard")
    dashboard()

    menu = {
        "View Project": lambda: view_project(),
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
