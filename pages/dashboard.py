import pandas as pd
import streamlit as st
from st_aggrid import AgGrid

import utils
from constants import *


def dashboard():
    st.write("Dashboard")

    # This works
    # # Create a sample dataframe
    # df = pd.DataFrame({'Name': ['Alice', 'Bob', 'Charlie'], 'Age': [25, 30, 35]})
    #
    # # Define a custom HTML template for each row
    # row_template = """
    # <div style="cursor: pointer">
    #   <div>{}</div>
    #   <div>{}</div>
    # </div>
    # """
    #
    # # Display the dataframe using the custom template
    # for index, row in df.iterrows():
    #     st.write(row_template.format(row['Name'], row['Age']), unsafe_allow_html=True)

    st.subheader("**Projects**")
    df_projects = pd.DataFrame(columns=PROJECT_COLUMNS)
    projects_info = st.session_state[PROJECTS]
    if projects_info.num_count > 0:
        # turn a class object to json dictionary to be processed by pandas dataframe
        df_projects = pd.DataFrame(projects_info.to_json()[PROJECTS])
        df_projects = df_projects[PROJECT_COLUMNS]

    AgGrid(df_projects)

    # # function to handle row clicks
    # # Add a callback function to handle clicks on the rows
    # def on_table_click(event):
    #     if event:
    #         # Get the index of the clicked row
    #         row_index = event['row']
    #
    #         # Get the data in the clicked row
    #         row_data = df_project_table.iloc[row_index]
    #
    #         # Do something with the data (for example, print it to the console)
    #         print('Clicked row:', row_data)
    #
    # table_project.add_rows(on_table_click)
    # st.dataframe(df_project_table)

    st.subheader("**Tasks**")
    json_tasks = utils.from_file("{\"num_count\":0,\"tasks\":[]}",
                                   # os.path.join(os.getcwd(), "data"),
                                   ADQ_WORKING_FOLDER,
                                   TASKS + JSON_EXT)

    df_tasks = pd.DataFrame(columns=TASK_COLUMNS)
    if len(json_tasks[TASKS]) > 0:
        df_tasks = pd.DataFrame(json_tasks[TASKS])
        df_tasks = df_tasks[TASK_COLUMNS]

    AgGrid(df_tasks)
