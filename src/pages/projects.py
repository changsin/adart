import datetime
import json
import os
import shutil

import streamlit as st

from src.common import utils
from src.common.constants import *
from src.common.convert_lib import convert_CVAT_to_Form
from src.home import select_project, get_projects_info
from src.models.projects_info import Project


def create_projects():
    with st.form("Create A Project"):
        name = st.text_input("**Name:**")
        images_folder = st.text_input("**Images folder:**")
        options = [SUPPORTED_IMAGE_FILE_EXTENSIONS,
                   SUPPORTED_VIDEO_FILE_EXTENSIONS,
                   SUPPORTED_AUDIO_FILE_EXTENSIONS,
                   "*", ""]
        selected_file_types = st.selectbox("**Image file types**",
                                           options,
                                           index=len(options) - 1)

        labels_folder = st.text_input("**Labels folder:**")
        labels_format_type = st.selectbox("**Choose format:**", SUPPORTED_FORMATS)
        submitted = st.form_submit_button("Create project")

        if submitted:
            st.markdown(f"**Name:** {name}")
            st.markdown(f"**Images folder:** {images_folder}")
            image_files = utils.generate_file_tree(images_folder, selected_file_types.split())

            st.markdown(f"**Labels folder:** {labels_folder}")
            patterns = ["*.xml"]
            if labels_format_type.endswith("JSON"):
                patterns = ["*.json"]

            label_files = utils.generate_file_tree(labels_folder, patterns)

            projects_info = st.session_state[PROJECTS]
            project_id = projects_info.get_next_project_id()

            target_folder = os.path.join(ADQ_WORKING_FOLDER, str(project_id))
            if not os.path.exists(target_folder):
                os.mkdir(target_folder)

            target_filenames = []
            for folder, files in label_files.items():
                for file in files:
                    anno_file = os.path.join(folder, file)
                    if labels_format_type == CVAT_XML:
                        target_filename = convert_CVAT_to_Form("NN", anno_file,
                                                               str(labels_format_type).lower(),
                                                               target_folder)
                        target_filenames.append(target_filename)
                    elif labels_format_type == ADQ_JSON:
                        ori_folder = os.path.join(target_folder, "origin")
                        if not os.path.exists(ori_folder):
                            os.mkdir(ori_folder)

                        target_filename = os.path.join(ori_folder, os.path.basename(anno_file))
                        shutil.copy(anno_file, target_filename)

                        target_filenames.append(target_filename)

            label_files_dict = {os.getcwd(): target_filenames}
            new_project = Project(project_id, name, image_files, label_files_dict,
                                  1, 1, str(datetime.datetime.now()))
            projects_info.add(new_project)

            utils.to_file(json.dumps(projects_info,
                                     default=utils.default, indent=2),
                          ADQ_WORKING_FOLDER,
                          PROJECTS + JSON_EXT)

            st.write("Project {} {} created".format(project_id, name))


def delete_project():
    selected_project = select_project()

    if selected_project:
        if st.button("Are you sure you want to delete the project {}-{}?"
                     .format(selected_project.id, selected_project.name)):
            # Your code to handle the user choosing not to proceed
            projects_info = get_projects_info()
            projects_info.projects.remove(selected_project)

            folder_path = os.path.join(ADQ_WORKING_FOLDER, str(selected_project.id))
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)
            st.markdown("**Deleted project {}-{}".format(selected_project.id, selected_project.name))

            utils.to_file(json.dumps(projects_info,
                                     default=utils.default, indent=2),
                          ADQ_WORKING_FOLDER,
                          PROJECTS + JSON_EXT)

            # TODO: Delete tasks too


def main():
    menu = {
        "Create Projects": lambda: create_projects(),
        "Delete Project": lambda: delete_project(),
    }

    # Create a sidebar with menu options
    selected_action = st.sidebar.radio("Choose action", list(menu.keys()))

    if selected_action:
        # Call the selected method based on the user's selection
        menu[selected_action]()


if __name__ == '__main__':
    main()
