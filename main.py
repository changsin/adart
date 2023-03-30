import fnmatch
import json
import os
import shutil

import pandas as pd
import streamlit as st
from st_aggrid import AgGrid

from convert_lib import convert_CVAT_to_Form

ADQ_WORKING_FOLDER = ".adq"
PROJECTS = "projects"
TASKS = "tasks"

SUPPORTED_FORMATS = ["CVAT XML", "PASCAL VOC XML", "COCO JSON"]
SUPPORTED_IMAGE_FILE_EXTENSIONS = ["*.jpg", "*.png", "*.tiff", "*.gif"]

def home():
    st.write("DaReT")


def from_file(str_default, folder, filename):
    full_path = os.path.join(folder, filename)
    if os.path.exists(full_path):
        file = open(full_path, 'r', encoding='utf-8')
        return json.load(file)

    return json.loads(str_default)


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

    st.subheader("Projects")
    # load_projects("{\"num_count\":0,\"projects\":[]}", ADQ_WORKING_FOLDER, PROJECTS + ".json")
    json_projects = from_file("{\"num_count\":0,\"projects\":[]}",
                              os.path.join(os.getcwd(), "data"),
                              "projects-sample1.json")
    df_projects = pd.DataFrame(json_projects["projects"])
    df_project_table = df_projects[['id', 'name', 'file_format_id', 'Total_count', 'task_count']]
    table_project = st.table(df_project_table)

    AgGrid(df_project_table)

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

    st.subheader("Tasks")
    json_tasks = from_file("{\"num_count\":0,\"tasks\":[]}",
                           os.path.join(os.getcwd(), "data"),
                           "tasks-sample1.json")

    df_tasks = pd.DataFrame(json_tasks["tasks"])
    st.table(df_tasks[['id', 'name', "project_id"]])


def get_folder_info(root, patterns):
    root_level = root.count("\\")

    folders_with_matches = {}
    for folder, sub_folders, filenames in os.walk(root):
        # st.write("{} has ({}) sub-folders with ({} files)".format(folder, len(sub_folders), len(filenames)))

        for pattern in patterns:
            matched = fnmatch.filter([filename.lower() for filename in filenames], pattern.lower())
            if matched:
                parent_folder = os.path.dirname(folder)
                if folders_with_matches.get(parent_folder):
                    folders_with_matches.pop(parent_folder)

                folders_with_matches[folder] = len(matched)

    for folder, count in folders_with_matches.items():
        current_level = folder.count("\\")
        level = current_level - root_level

        str_out = " "
        for _ in range(level):
            str_out += " "

        st.markdown("{}- {} ({})".format(str_out, folder, count))

    return list(folders_with_matches.keys())


def create_projects():
    with st.form("Create A Project"):
        name = st.text_input("Name")
        images_folder = st.text_input("Images folder")
        labels_folder = st.text_input("Labels folder")
        format_type = st.selectbox("Choose format", SUPPORTED_FORMATS)
        submitted = st.form_submit_button("Create project")

        if submitted:
            # Do something with the user's inputs
            st.write(f"Name: {name}")
            st.markdown(f"**Images folder: {images_folder}**")
            get_folder_info(images_folder, SUPPORTED_IMAGE_FILE_EXTENSIONS)

            st.markdown(f"**Labels folder: {labels_folder}**")
            labels_folders = [labels_folder]
            if format_type.endswith("json"):
                labels_folders.extend(get_folder_info(labels_folder, ["*.json"]))
            else:
                labels_folders.extend(get_folder_info(labels_folder, ["*.xml"]))

            project_id = "1"
            destination_folder = os.path.join(ADQ_WORKING_FOLDER, project_id)
            if not os.path.exists(destination_folder):
                os.mkdir(destination_folder)

            for folder_to_convert in labels_folders:
                convert_CVAT_to_Form("NN", folder_to_convert, str(format_type).lower(), destination_folder)


def create_tasks():
    with st.form("Create Tasks"):
        sample_percent = st.text_input("% of samples")

        st.form_submit_button("Create tasks")


def start_st():
    if not os.path.exists(ADQ_WORKING_FOLDER):
        os.mkdir(ADQ_WORKING_FOLDER)

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
    # dashboard()
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
