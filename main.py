import json
import os

import pandas as pd
import streamlit as st

ADQ_WORKING_FOLDER = ".adq"
PROJECTS = "projects"
TASKS = "tasks"


def home():
    st.write("DaRe")


def from_file(str_default, folder, filename):
    full_path = os.path.join(folder, filename)
    if os.path.exists(full_path):
        file = open(full_path, 'r', encoding='utf-8')
        return json.load(file)

    return json.loads(str_default)


def dashboard():
    st.write("Dashboard")

    st.subheader("Projects")
    # load_projects("{\"num_count\":0,\"projects\":[]}", ADQ_WORKING_FOLDER, PROJECTS + ".json")
    json_projects = from_file("{\"num_count\":0,\"projects\":[]}",
                              os.path.join(os.getcwd(), "data"),
                              "projects-sample1.json")
    df_projects = pd.DataFrame(json_projects["projects"])
    st.table(df_projects[['id', 'name', 'file_format_id', 'Total_count', 'task_count']])

    st.subheader("Tasks")
    json_tasks = from_file("{\"num_count\":0,\"tasks\":[]}",
                           os.path.join(os.getcwd(), "data"),
                           "tasks-sample1.json")

    df_tasks = pd.DataFrame(json_tasks["tasks"])
    # st.table(df_tasks[['id', 'name', "project_id"]])
    st.write(df_tasks)


def create_projects():
    with st.form("Create A Project"):
        name = st.text_input("Name")
        images_folder = st.text_input("Images folder")
        labels_folder = st.text_input("Labels folder")
        submitted = st.form_submit_button("Create project")

        if submitted:
            # Do something with the user's inputs
            st.write(f"Name: {name}")
            st.write(f"Images folder: {images_folder}")
            st.write(f"Labels folder: {labels_folder}")


def create_tasks():
    with st.form("Create Tasks"):
        sample_percent = st.text_input("% of samples")

        st.form_submit_button("Create tasks")


def start_st():
    st.sidebar.header("Data Reviewer")

    menu = {
        "Home": dashboard,
        "Dashboard": dashboard,
        "Create Projects": create_projects,
        "Create Tasks": create_tasks
    }

    # Create a sidebar with menu options
    selected = st.sidebar.selectbox("Select an option", list(menu.keys()))

    # Call the selected method based on the user's selection
    menu[selected]()


if __name__ == '__main__':
    start_st()
    # json_projects = load_projects("{\"num_count\":0,\"projects\":[]}",
    #                               os.path.join(os.getcwd(), "data"),
    #                               "project-sample1.json")
    # print(pd.DataFrame(json_projects["projects"]))
    # json_tasks = from_file("{\"num_count\":0,\"tasks\":[]}",
    #                         os.path.join(os.getcwd(), "data"),
    #                        "task-sample1.json")
    # df_tasks = pd.DataFrame(json_tasks["tasks"])
    # print(df_tasks[['id', 'name', "project_id"]])
