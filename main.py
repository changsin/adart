import datetime
import fnmatch
import json
import os
import shutil
from pathlib import Path
from projects import Project

import pandas as pd
import streamlit as st
from st_aggrid import AgGrid

from convert_lib import convert_CVAT_to_Form

ADQ_WORKING_FOLDER = ".adq"
PROJECTS = "projects"
TASKS = "tasks"
JSON_EXT = ".json"

CVAT_XML = "CVAT XML"
PASCAL_VOC_XML = "PASCAL VOC XML"
COCO_JSON = "COCO JSON"
ADQ_JSON = "ADQ JSON"

SUPPORTED_FORMATS = [CVAT_XML, PASCAL_VOC_XML, COCO_JSON, ADQ_JSON]
SUPPORTED_IMAGE_FILE_EXTENSIONS = ["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.tiff", "*.gif"]

PROJECT_COLUMNS = ['id', 'name', 'file_format_id',
                   'total_count', 'task_total_count', 'task_done_count']

TASK_COLUMNS = ['id', 'name', "project_id"]

dart = None


def home():
    st.write("DaRT")


def from_file(str_default, folder, filename):
    full_path = os.path.join(folder, filename)
    if os.path.exists(full_path):
        file = open(full_path, 'r', encoding='utf-8')
        return json.load(file)

    return json.loads(str_default)

def to_file(data, folder, filename):
    """
    save data to path
    """
    full_path = os.path.join(folder, filename)
    with open(full_path,  'w', encoding="utf-8") as json_file:
        json_file.write(data)


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
                              # os.path.join(os.getcwd(), "data"),
                              ADQ_WORKING_FOLDER,
                              PROJECTS + JSON_EXT)
    df_projects = pd.DataFrame(columns=PROJECT_COLUMNS)
    if len(json_projects[PROJECTS]) > 0:
        df_projects = pd.DataFrame(json_projects[PROJECTS])
        df_projects = df_projects[df_projects.columns]

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

    st.subheader("Tasks")
    json_tasks = from_file("{\"num_count\":0,\"tasks\":[]}",
                           # os.path.join(os.getcwd(), "data"),
                           ADQ_WORKING_FOLDER,
                           TASKS + JSON_EXT)

    df_tasks = pd.DataFrame(columns=TASK_COLUMNS)
    if len(json_tasks[TASKS]) > 0:
        df_tasks = pd.DataFrame(json_tasks[TASKS])
        df_tasks = df_tasks[json_tasks.columns]

    AgGrid(df_tasks)

    # dart = Dart()


def generate_file_tree(folder_path, patterns):
    file_tree_to_return = []
    for root, dirs, files in os.walk(folder_path):
        level = root.replace(folder_path, '').count(os.sep)
        indent = '-' * 4 * (level)

        for pattern in patterns:
            matched = fnmatch.filter([filename.lower() for filename in files], pattern.lower())
            if matched:
                st.markdown('{}📁{}({})/'.format(indent, root.replace(folder_path, ''), len(matched)))
                for filename in matched:
                    if not os.path.isdir(filename):
                        file_tree_to_return.append(os.path.join(root, filename))

    return file_tree_to_return


def get_next_project_id(projects):
    if len(projects) == 0:
        return 0

    project_idx = []
    for project in projects:
        project_idx.append(project["id"])

    return max(project_idx) + 1


def create_projects():
    with st.form("Create A Project"):
        name = st.text_input("**Name:**")
        images_folder = st.text_input("**Images folder:**")
        images_format_type = st.selectbox("**Image file types**",
                                   ["*.jpg *.jpeg *.png *.bmp *.tiff *.gif",
                                    "*.wav",
                                    "*"])
        labels_folder = st.text_input("**Labels folder:**")
        labels_format_type = st.selectbox("**Choose format:**", SUPPORTED_FORMATS)
        submitted = st.form_submit_button("Create project")

        if submitted:
            # Do something with the user's inputs
            st.markdown(f"**Name:** {name}")
            st.markdown(f"**Images folder:** {images_folder}")
            # get_folder_info(images_folder, SUPPORTED_IMAGE_FILE_EXTENSIONS)
            # show_dir_tree(Path(images_folder))
            # files_tree = generate_file_tree(images_folder)
            # display_file_tree(files_tree, indent=2)
            print(images_format_type)
            generate_file_tree(images_folder, images_format_type.split())

            st.markdown(f"**Labels folder:** {labels_folder}")
            patterns = ["*.xml"]
            if labels_format_type.endswith("JSON"):
                patterns = ["*.json"]

            label_files = generate_file_tree(labels_folder, patterns)

            json_projects = from_file("{\"num_count\":0,\"projects\":[]}",
                                      ADQ_WORKING_FOLDER,
                                      PROJECTS + JSON_EXT)
            projects = json_projects[PROJECTS]
            project_id = get_next_project_id(projects)

            # from_file()
            destination_folder = os.path.join(ADQ_WORKING_FOLDER, str(project_id))
            if not os.path.exists(destination_folder):
                os.mkdir(destination_folder)

            for anno_file in label_files:
                if labels_format_type == CVAT_XML:
                    convert_CVAT_to_Form("NN", anno_file,
                                         str(labels_format_type).lower(), destination_folder)
                elif labels_format_type == ADQ_JSON:
                    ori_folder = os.path.join(destination_folder, "origin")
                    if not os.path.exists(ori_folder):
                        os.mkdir(ori_folder)

                    shutil.copy(anno_file,
                                os.path.join(ori_folder, os.path.basename(anno_file)))

            # TODO: need to deserialize and serialize projects
            # new_project = Project(project_id, name, images_folder, labels_folder, 1, 1, str(datetime.datetime.now()))
            # projects.append(json.dumps(new_project))
            #
            # to_file(projects, ADQ_WORKING_FOLDER, PROJECTS + JSON_EXT)


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
