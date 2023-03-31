import fnmatch
import json
import os
import shutil
from pathlib import Path

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


dart = None

def home():
    st.write("DaRT")


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
                              # os.path.join(os.getcwd(), "data"),
                              ADQ_WORKING_FOLDER,
                              PROJECTS + JSON_EXT)
    df_projects = pd.DataFrame(json_projects[PROJECTS])
    df_project_table = df_projects[['id', 'name', 'file_format_id', 'total_count', 'task_total_count', 'task_done_count']]
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
                           # os.path.join(os.getcwd(), "data"),
                           ADQ_WORKING_FOLDER,
                           TASKS + JSON_EXT)

    df_tasks = pd.DataFrame(json_tasks[TASKS])
    st.table(df_tasks[['id', 'name', "project_id"]])

    # dart = Dart()

def generate_file_tree(startpath):
    """
    Recursively generates a dictionary of the file tree starting at the specified path.
    """
    file_tree = {}
    for root, dirs, files in os.walk(startpath):
        # remove hidden files/directories
        dirs = [d for d in dirs if not d.startswith('.')]
        files = [f for f in files if not f.startswith('.')]
        if files or dirs:
            current_level = file_tree
            # split the current path into components and add them to the file tree
            for component in os.path.relpath(root, startpath).split(os.path.sep):
                print("current_level before: {} startpath:{}".format(current_level, startpath))
                current_level = current_level.setdefault(component, {})
                print("current_level after: {} component:{}".format(current_level, component))
            # add the files at this level
            # for file in files:
            #     current_level[file] = None
    return file_tree


def display_file_tree(file_tree, indent=0):
    """
    Recursively displays the file tree in a formatted way using Streamlit's st.write function.
    """
    print(file_tree)
    count = 0
    for key, value in file_tree.items():
        if value is None:
            # st.write('-' * indent + '- ' + key)
            count += 1
        else:
            file_count = display_file_tree(value, indent + 2)
            st.write('-' * indent + '+ ' + key + '/' + "({})".format(file_count))

    return count


tee = '\u251C'  # ├
last = '\u2514'  # └
branch = '\u2502'  # │
space = ' '  # space character


def tree(dir_path: Path, prefix: str = ''):
    """A recursive generator, given a directory Path object
    will yield a visual tree structure line by line
    with each line prefixed by the same characters
    """
    contents = list(dir_path.iterdir())
    # contents each get pointers that are ├── with a final └── :
    pointers = [tee] * (len(contents) - 1) + [last]
    for pointer, path in zip(pointers, contents):
        yield prefix + pointer + path.name
        if path.is_dir():  # extend the prefix and recurse:
            extension = branch if pointer == tee else space
            # i.e. space because last, └── , above so no more |
            yield from tree(path, prefix=prefix + extension)


# def get_dirs_inside_dir(folder):
#     return [my_dir for my_dir in list(map(lambda x:os.path.basename(x), sorted(Path(folder).iterdir(), key=os.path.getmtime, reverse=True))) if os.path.isdir(os.path.join(folder, my_dir))
#             and my_dir != '__pycache__' and my_dir != '.ipynb_checkpoints' and my_dir != 'API']


# def list_folders_in_folder(folder):
#     return [file for file in os.listdir(folder) if os.path.isdir(os.path.join(folder, file))]


def show_dir_tree(folder):
    with st.expander(f"Show {os.path.basename(folder)} folder tree"):
        # for line in tree(Path.home() / folder):
        for line in tree(folder):
            st.write(line)


def get_folder_info(root, patterns):
    root_level = root.count(os.path.sep)

    folders_with_matches = {}
    for folder, sub_folders, filenames in os.walk(root):
        # st.write("{} has ({}) sub-folders with ({} files)".format(folder, len(sub_folders), len(filenames)))

        for pattern in patterns:
            matched = fnmatch.filter([filename.lower() for filename in filenames], pattern.lower())
            if matched:
                parent_folder = os.path.dirname(folder)
                if folders_with_matches.get(parent_folder):
                    # folders_with_matches.pop(parent_folder)
                    folders_with_matches[parent_folder] = 0

                folders_with_matches[folder] = len(matched)

    for folder, count in folders_with_matches.items():
        current_level = folder.count(os.path.sep)
        level = current_level - root_level

        icon = "📁"
        if count > 0:
            icon = "📄"

        folder = folder.removeprefix(root)

        st.markdown("{} {} {} ({})".format(" " * level, icon, folder, count))

    return list(folders_with_matches.keys())


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
        # sub_indent = '-' * 4 * (level + 1)
        # file_tree.append('{}{}'.format(sub_indent, len(files)))
        # for file in files:
        #     file_tree.append('{}{}'.format(sub_indent, file))

    return file_tree_to_return


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
            # get_folder_info(images_folder, SUPPORTED_IMAGE_FILE_EXTENSIONS)
            # show_dir_tree(Path(images_folder))
            # files_tree = generate_file_tree(images_folder)
            # display_file_tree(files_tree, indent=2)
            generate_file_tree(images_folder, SUPPORTED_IMAGE_FILE_EXTENSIONS)

            st.markdown(f"**Labels folder: {labels_folder}**")
            patterns = ["*.xml"]
            if format_type.endswith("JSON"):
                patterns = ["*.json"]

            label_files = generate_file_tree(labels_folder, patterns)

            project_id = "1"
            destination_folder = os.path.join(ADQ_WORKING_FOLDER, project_id)
            if not os.path.exists(destination_folder):
                os.mkdir(destination_folder)

            for anno_file in label_files:
                if format_type == CVAT_XML:
                    convert_CVAT_to_Form("NN", anno_file, str(format_type).lower(), destination_folder)
                elif format_type == ADQ_JSON:
                    ori_folder = os.path.join(destination_folder, "origin")
                    if not os.path.exists(ori_folder):
                        os.mkdir(ori_folder)

                    shutil.copy(anno_file,
                                os.path.join(ori_folder, os.path.basename(anno_file)))

            # json_projects = from_file("{\"num_count\":0,\"projects\":[]}",
            #                           ADQ_WORKING_FOLDER,
            #                           PROJECTS + JSON_EXT)
            # from_file()


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
