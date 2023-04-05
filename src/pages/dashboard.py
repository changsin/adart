import pandas as pd
import streamlit as st
from st_aggrid import AgGrid

from src.common import constants, utils
from src.home import get_projects_info


def main():
    st.write("Dashboard")

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


if __name__ == '__main__':
    main()
