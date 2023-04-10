import datetime
import importlib.util
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
from src.common.constants import (
    SUPPORTED_AUDIO_FILE_EXTENSIONS,
    SUPPORTED_IMAGE_FILE_EXTENSIONS,
    SUPPORTED_VIDEO_FILE_EXTENSIONS,
    SUPPORTED_FORMATS,

    ADQ_WORKING_FOLDER,
    PASCAL_VOC_XML,
    CVAT_XML,
    ADQ_JSON,

    DomainCode
)
from src.common.convert_lib import convert_CVAT_to_Form, convert_PASCAL_to_Form
from src.home import select_project, get_projects_info, get_tasks_info
from src.models.projects_info import Project, ModelProject

MULTI_SELECT_SEP = ';'


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

                            json_data = utils.from_file("{}",
                                                        folder,
                                                        file)
                            if not json_data:
                                st.write("Skipping {} - empty file".format(file))
                                continue

                            if not json_data.get("twconverted"):
                                st.write("Skipping {} - not a valid adq label file".format(file))
                                continue

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

        model_type = st.multiselect("Model type", ["Object recognition", "Object detection", "Motion detection", "NLP"])
        models_used = st.text_input("Models used (YOLOv5, etc. separated by semi-colons)")

        default_options = ["Unstructured", "Structured"]
        default_index = default_options.index("Unstructured")
        data_type = st.radio("Data type", default_options, index=default_index)
        data_format = st.multiselect("Data format", ["image", "video", "audio", "text", "number"])

        domain = st.multiselect("Domain", DomainCode.get_all_types())
        cost = st.number_input("Cost", step=10000, format="%d")

        submitted = st.form_submit_button("Create project")
        if submitted:
            if not project_name or len(project_name) == 0:
                st.warning("Please enter a project name")
                return

            new_project_id = get_projects_info().get_next_project_id()

            model_project = ModelProject(MULTI_SELECT_SEP.join(model_type),
                                         models_used,
                                         data_type,
                                         MULTI_SELECT_SEP.join(data_format),
                                         MULTI_SELECT_SEP.join(domain),
                                         cost=cost)

            new_project = Project(new_project_id, project_name, {}, {},
                                  0, 0, str(datetime.datetime.now()),
                                  customer_company=company_name,
                                  customer_name=company_contact_person,
                                  customer_url=company_url,
                                  customer_email=company_contact_person_email,
                                  customer_phone=company_contact_person_phone,
                                  customer_address=company_address,
                                  extended_properties=model_project)

            target_folder = os.path.join(ADQ_WORKING_FOLDER, str(new_project_id))
            if not os.path.exists(target_folder):
                os.mkdir(target_folder)

            projects_info = get_projects_info()
            projects_info.add(new_project)
            projects_info.save()

            st.write("Project {} {} created".format(new_project_id, project_name))


def delete_project():
    selected_project = select_project(is_sidebar=True)

    if selected_project:
        delete_confirmed = st.sidebar.button("Are you sure you want to delete the project {}-{}?"
                                             .format(selected_project.id, selected_project.name))
        if delete_confirmed:
            # Delete the artifacts first
            folder_path = os.path.join(ADQ_WORKING_FOLDER, str(selected_project.id))
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)

            # Then all the tasks
            tasks_info = get_tasks_info()
            for selected_task in tasks_info.tasks:
                if selected_task.project_id == selected_project.id:
                    tasks_info.tasks.remove(selected_task)
            tasks_info.save()

            # Finally delete the project itself
            projects_info = get_projects_info()
            projects_info.projects.remove(selected_project)

            st.markdown("## Deleted project {} {}".format(selected_project.id, selected_project.name))
            projects_info.save()


def update_project():
    selected_project = select_project(is_sidebar=True)
    if selected_project:
        if selected_project.extended_properties:
            update_model_project(selected_project)
        else:
            update_data_project(selected_project)


def update_data_project(selected_project: Project):
    st.sidebar.write("Coming soon")


def update_model_project(selected_project: Project):
    with st.form("Update Model Validation Project"):
        project_name = st.text_input("**Name:**", selected_project.name)

        model_project_props = selected_project.extended_properties

        company_name = st.text_input("**Company Name:**", selected_project.customer_company)
        company_url = st.text_input("**Company URL:**", selected_project.customer_url)
        company_address = st.text_input("**Company address:**", selected_project.customer_address)
        company_contact_person = st.text_input("**Contact person**", selected_project.customer_name)
        company_contact_person_email = st.text_input("**Contact person email:**",
                                                     selected_project.customer_email)
        company_contact_person_phone = st.text_input("**Contact person phone number:**",
                                                     selected_project.customer_phone)

        default_options = None
        if model_project_props.model_type:
            default_options = [model_type for model_type in model_project_props.model_type.split(MULTI_SELECT_SEP)]
        model_type = st.multiselect("Model type",
                                    default=default_options,
                                    options=["Object recognition", "Object detection", "Motion detection", "NLP"])
        models_used = st.text_input("Models used (YOLOv5, etc. separated by commas)",
                                    model_project_props.models_used)

        default_options = ["Unstructured", "Structured"]
        default_index = default_options.index(model_project_props.data_type)
        data_type = st.radio("Data type", default_options,
                             index=default_index)
        default_options = [data_format for data_format in model_project_props.data_format.split(MULTI_SELECT_SEP)]
        data_format = st.multiselect("Data format", ["image", "video", "audio", "text", "number"],
                                     default=default_options)

        default_options = None
        if model_project_props.model_type:
            default_options = [domain for domain in model_project_props.domain.split(MULTI_SELECT_SEP)]
        domain = st.multiselect("Domain", default=default_options,
                                options=DomainCode.get_all_types())

        cost = st.number_input("Cost",
                               value=int(model_project_props.cost),
                               min_value=int(0), max_value=int(999999999),
                               step=int(utils.step_size(10000)), format="%d")

        submitted = st.form_submit_button("Update project")
        if submitted:
            if not project_name or len(project_name) == 0:
                st.warning("Please enter a project name")
                return

            model_project_props = ModelProject(MULTI_SELECT_SEP.join(model_type),
                                               models_used,
                                               data_type,
                                               MULTI_SELECT_SEP.join(data_format),
                                               MULTI_SELECT_SEP.join(domain),
                                               cost=cost)
            selected_project.name = project_name
            selected_project.customer_company = company_name
            selected_project.customer_name = company_contact_person
            selected_project.customer_url = company_url
            selected_project.customer_email = company_contact_person_email
            selected_project.customer_phone = company_contact_person_phone,
            selected_project.customer_address = company_address,
            selected_project.extended_properties = model_project_props

            projects_info = get_projects_info()
            projects_info.update_project(selected_project)
            projects_info.save()

            st.write("Project {} {} updated".format(selected_project.id, project_name))


def create_project():
    menu = {
        "data": lambda: create_data_project(),
        "model": lambda: create_model_project(),
    }

    # Create a sidebar with menu options
    selected_project_type = st.sidebar.selectbox("Project type", list(menu.keys()))
    if selected_project_type:
        # Call the selected method based on the user's selection
        menu[selected_project_type]()


def main():
    menu = {
        "Create Project": lambda: create_project(),
        "Update Project": lambda: update_project(),
        "Delete Project": lambda: delete_project()
    }

    # Create a sidebar with menu options
    selected_action = st.sidebar.radio("Choose action", list(menu.keys()))
    if selected_action:
        # Call the selected method based on the user's selection
        menu[selected_action]()


if __name__ == '__main__':
    main()
