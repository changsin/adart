import importlib.util
import importlib.util

import pandas as pd
import streamlit as st
from st_aggrid import AgGrid

spec = importlib.util.find_spec("src")
if spec is None:
    import sys
    from pathlib import Path

    path_root = Path(__file__).parents[2]
    sys.path.append(str(path_root))

from src.common import constants, utils
from src.home import get_projects_info, select_project, get_df_tasks


def view_project():
    selected_project = select_project(is_sidebar=True)

    if selected_project:
        st.markdown("# Project")

        extended_props = selected_project.extended_properties
        df_project = pd.DataFrame.from_dict(selected_project)
        st.dataframe(df_project)

        if extended_props:
            st.markdown("## Model validation information")
            st.dataframe(pd.DataFrame.from_dict(extended_props,
                                                orient='index'))

        st.markdown("# Tasks")
        df_tasks = get_df_tasks(selected_project.id)
        st.dataframe(df_tasks.transpose())


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
    json_tasks = utils.from_file("{\"num_count\":0,\"tasks\":[]}",
                                 # os.path.join(os.getcwd(), "data"),
                                 constants.ADQ_WORKING_FOLDER,
                                 constants.TASKS + constants.JSON_EXT)

    df_tasks = pd.DataFrame(columns=constants.TASK_COLUMNS)
    if len(json_tasks[constants.TASKS]) > 0:
        df_tasks = pd.DataFrame(json_tasks[constants.TASKS])
        df_tasks = df_tasks[constants.TASK_COLUMNS]

    AgGrid(df_tasks)


def main():
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
    main()
