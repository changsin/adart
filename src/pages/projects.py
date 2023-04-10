import datetime
import importlib.util
import json
import os
import shutil
from pathlib import Path

import streamlit as st

spec = importlib.util.find_spec("src")
if spec is None:
    import sys

    path_root = Path(__file__).parents[2]
    sys.path.append(str(path_root))

from src.common import utils
from src.common.constants import *
from src.common.convert_lib import convert_CVAT_to_Form, convert_PASCAL_to_Form
from src.home import select_project, get_projects_info
from src.models.projects_info import Project


def create_data_project():
    with st.form("Create a Data Project"):
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
            data_files = utils.generate_file_tree(images_folder, selected_file_types.split())

            st.markdown(f"**Labels folder:** {labels_folder}")
            patterns = ["*.xml"]
            if labels_format_type.endswith("JSON"):
                patterns = ["*.json"]

            label_files = utils.generate_file_tree(labels_folder, patterns)

            projects_info = get_projects_info()
            project_id = projects_info.get_next_project_id()

            target_folder = os.path.join(ADQ_WORKING_FOLDER, str(project_id))
            if not os.path.exists(target_folder):
                os.mkdir(target_folder)

            target_filenames = []
            if labels_format_type == PASCAL_VOC_XML:
                for folder, files in label_files.items():
                    anno_files = [os.path.join(folder, file) for file in files]
                    target_filename = convert_PASCAL_to_Form("11", anno_files, target_folder)
                    target_filenames.append(os.path.basename(target_filename))
            else:
                for folder, files in label_files.items():
                    for file in files:
                        anno_file = os.path.join(folder, file)
                        if labels_format_type == CVAT_XML:
                            target_filename = convert_CVAT_to_Form("NN", anno_file,
                                                                   target_folder)
                            target_filenames.append(os.path.basename(target_filename))
                        elif labels_format_type == ADQ_JSON:
                            ori_folder = os.path.join(target_folder, "origin")
                            if not os.path.exists(ori_folder):
                                os.mkdir(ori_folder)

                            target_filename = os.path.join(ori_folder, os.path.basename(anno_file))
                            shutil.copy(anno_file, target_filename)

                            target_filenames.append(os.path.basename(target_filename))

            label_files_dict = {target_folder: target_filenames}
            new_project = Project(project_id, name, data_files, label_files_dict,
                                  1, 1, str(datetime.datetime.now()))
            projects_info.add(new_project)
            projects_info.save()
            st.write("Project {} {} created".format(project_id, name))


def create_model_project():
    with st.form("Create Model Validation Project"):
        project_name = st.text_input("**Name:**")

        company_name = st.text_input("**Company Name:**")
        company_url = st.text_input("**Company URL:**")
        company_address = st.text_input("**Company address:**")
        company_contact_person = st.text_input("**Contact person**")
        company_contact_person_email = st.text_input("**Contact person email:**")
        company_contact_person_phone = st.text_input("**Contact person phone number:**")

        domain = st.selectbox("Domain", ["Object recognition", "Motion "])

        contacted_date = st.date_input("**Contacted:**")
        uploaded_contacted_artifacts = st.file_uploader("Upload contacted artifacts", accept_multiple_files=True)

        new_project_id = get_projects_info().get_next_project_id()

        save_folder = os.path.join(ADQ_WORKING_FOLDER, str(new_project_id))
        if not os.path.exists(save_folder):
            os.mkdir(save_folder)

        if uploaded_contacted_artifacts:
            # Save the uploaded file
            with open(os.path.join(save_folder, uploaded_contacted_artifacts.name), "wb") as f:
                f.write(uploaded_contacted_artifacts.getbuffer())

        test_date = st.date_input("**Test date**")
        uploaded_test_artifacts = st.file_uploader("Upload test artifacts", accept_multiple_files=True)
        if uploaded_test_artifacts:
            for file in uploaded_test_artifacts:
                # Save each uploaded file
                with open(os.path.join(save_folder, file.name), "wb") as f:
                    f.write(file.getbuffer())

        submitted = st.form_submit_button("Create project")
        if submitted:

            st.write("Project {} {} created".format(new_project_id, project_name))


def delete_project():
    selected_project = select_project(is_sidebar=True)

    if selected_project:
        delete_confirmed = st.sidebar.button("Are you sure you want to delete the project {}-{}?"
                                             .format(selected_project.id, selected_project.name))
        if delete_confirmed:
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
        "Create Data Project": lambda: create_data_project(),
        "Create Model Project": lambda: create_model_project(),
        "Delete Project": lambda: delete_project()
    }

    # Create a sidebar with menu options
    selected_action = st.sidebar.radio("Choose action", list(menu.keys()))

    if selected_action:
        # Call the selected method based on the user's selection
        menu[selected_action]()


if __name__ == '__main__':
    main()
