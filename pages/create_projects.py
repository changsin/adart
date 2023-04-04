import datetime
import json
import os
import shutil

import streamlit as st

from common import utils
from common.constants import *
from common.convert_lib import convert_CVAT_to_Form
from models.projects_info import Project


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
            # get_folder_info(images_folder, SUPPORTED_IMAGE_FILE_EXTENSIONS)
            # show_dir_tree(Path(images_folder))
            # files_tree = generate_file_tree(images_folder)
            # display_file_tree(files_tree, indent=2)
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
            # NB: add as a json dict to make manipulating in pandas dataframe easier
            projects_info.add(new_project.to_json())

            utils.to_file(json.dumps(projects_info,
                                     default=utils.default, indent=2),
                          ADQ_WORKING_FOLDER,
                          PROJECTS + JSON_EXT)

            st.write("Project {} {} created".format(project_id, name))
