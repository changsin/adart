import os.path
from base64 import b64encode

import cv2
import numpy as np
import streamlit as st
from PIL import Image

import src.viewer.app as app
from src.common.constants import SUPPORTED_IMAGE_FILE_EXTENSIONS
from src.common.logger import get_logger
from src.common.utils import glob_files, load_images
from src.models.data_labels import DataLabels
from src.models.metrics import (
    cluster_images,
    reduce_features,
    plot_image_clusters
)
from .home import (
    get_data_files,
    get_label_files,
    is_authenticated,
    login,
    logout,
    select_project,
    select_task)

logger = get_logger(__name__)


@st.cache_resource
def load_thumbnail(file_path):
    with Image.open(file_path) as image:
        return image.copy()


def show_images(project_folder):
    thumbnail_filenames = get_data_files(project_folder, is_thumbnails=True)
    logger.info(f"{project_folder} {thumbnail_filenames}")
    # Define the number of columns
    num_columns = 5

    columns = st.columns(num_columns)
    for i, file in enumerate(thumbnail_filenames["."]):
        with columns[i % num_columns]:
            thumbnail_image = load_thumbnail(file)
            st.image(thumbnail_image, width=100)
            truncated_name = os.path.basename(file)[:20] + "..." if len(
                os.path.basename(file)) > 20 else os.path.basename(file)
            if st.button(truncated_name, key=f'{truncated_name}_{i}'):
                full_size_filename = os.path.join(project_folder, "data", os.path.basename(file))
                full_size_image = Image.open(full_size_filename)
                st.image(full_size_image, caption="Full-size Image")


def review_images():
    selected_project = select_project(is_sidebar=True)
    if selected_project:
        show_images(selected_project.dir_name)


def review_task():
    selected_project = select_project(is_sidebar=True)
    if selected_project:
        selected_task = select_task(selected_project.id)
        if selected_task:
            if selected_project.extended_properties:
                review_model_task(selected_task)
            else:
                # # Navigate to a new page with the task details
                # st.experimental_set_query_params(task_id=selected_task.id)
                app.main(selected_task)


def compare_tasks():
    selected_project = select_project(is_sidebar=True)
    if selected_project:
        task1 = select_task(selected_project.id, label="Select task1")
        task2 = select_task(selected_project.id, label="Select task2")

        if task1 and task2:
            col1, col2 = st.columns(2)

            with col1:
                app.main(task1)
            with col2:
                app.main(task2, is_second_viewer=True)


def review_model_task(selected_task):
    if selected_task.data_files and len(selected_task.data_files) > 0:
        for folder, files in selected_task.data_files.items():
            for file in files:
                st.write("📄{}".format(file))
                basename, extension = os.path.splitext(file)
                if extension.lower() == ".pdf":
                    pdf_file = open(os.path.join(folder, file), "rb").read()
                    # Embed the PDF file in an iframe
                    pdf_url = "data:application/pdf;base64," + b64encode(pdf_file).decode("utf-8")
                    st.write(f'<iframe src="{pdf_url}" width="700" height="1000"></iframe>', unsafe_allow_html=True)
                elif extension.lower() in SUPPORTED_IMAGE_FILE_EXTENSIONS:
                    st.image(os.path.join(folder, file))
                elif extension.lower() in [".docx", ".doc"]:
                    word_file = open(os.path.join(folder, file), "rb").read()
                    # Embed the Word document in an iframe using HTML tags
                    word_url = "data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64," + b64encode(
                        word_file).decode("utf-8")
                    st.markdown(f'<iframe https://view.officeapps.live.com/op/embed.aspx?src="{word_url}" width="700" height="1000"></iframe>', unsafe_allow_html=True)
    else:
        st.write("No uploaded files to review")


OVERLAPS = "Overlaps"
TINY_OBJECTS = "Tiny objects"
CLUSTER_LABELS = "Cluster labels"


def create_label_thumbnail(image: Image, label_object: DataLabels.Object, target_size: tuple=(50, 50)):
    """init annotation for current shapes.

    Args:
        :param image: PIL image
        :param label_object: label object
    Returns:
            prev_img: PIL image of the preview thumbnail.
    """
    raw_image = np.asarray(image).astype("uint8")
    height, width, alpha = raw_image.shape
    width = max(width, 1)
    height = max(height, 1)
    prev_img = np.zeros((height, width, alpha), dtype="uint8")

    if label_object.type == 'box':
        point_list = label_object.points[0]
        x, y, w, h = (
            int(point_list[0]),
            int(point_list[1]),
            int(point_list[2]),
            int(point_list[3])
        )
        x = max(x, 0)
        y = max(y, 0)
        w = max(w, 1)
        h = max(h, 1)

        x_end = min(x + w, height)
        y_end = min(y + h, width)

        prev_img[y:y_end, x:x_end] = raw_image[y:y_end, x:x_end]
        prev_img = prev_img[y:y_end, x:x_end]
    elif label_object.type == 'spline' or label_object.type == 'boundary' or label_object.type == 'polygon':
        if label_object.points:
            min_x, min_y, max_x, max_y = DataLabels.Object.get_bounding_rectangle(label_object)
            min_x = max(min_x, 0)
            min_y = max(min_y, 0)
            max_x = min(max_x, width)
            max_y = min(max_y, height)

            prev_img[min_y:max_y, min_x:max_x] = raw_image[min_y:max_y, min_x:max_x]
            prev_img = prev_img[min_y:max_y, min_x:max_x]
    elif label_object.type == 'VP':
        return None

    # Resize prev_img to target_size
    prev_img_resized = cv2.resize(prev_img, target_size[::-1])

    return prev_img_resized


def generate_label_thumbnails(data_folder: str, data_labels: DataLabels, label_thumbnail_folder: str):
    label_thumbnails = []
    thumbnail_names = []

    if os.path.exists(label_thumbnail_folder):
        thumbnail_names = glob_files(label_thumbnail_folder,
                                     SUPPORTED_IMAGE_FILE_EXTENSIONS)
        thumbnail_names.sort()
        label_thumbnails = load_images(thumbnail_names)
    else:
        os.mkdir(label_thumbnail_folder)

        for label_image in data_labels.images:
            image_filename = os.path.join(data_folder, label_image.name)
            image = Image.open(image_filename)
            for idx, obj in enumerate(label_image.objects):
                thumbnail_name = os.path.join(label_thumbnail_folder,
                                              f"{obj.label}{idx}-{label_image.name}")
                label_thumbnail = create_label_thumbnail(image, obj)
                if label_thumbnail:
                    label_thumbnail.save(thumbnail_name)

                    label_thumbnails.append(label_thumbnail)
                    thumbnail_names.append(thumbnail_name)

        thumbnail_names.sort()

    return label_thumbnails, thumbnail_names


def detect_label_anomalies(selected_project):
    """
    run cluster analysis on label images
    :return:
    """
    label_files_dict = get_label_files(selected_project)
    class_labels = set()
    label_thumbnails = []
    thumbnail_names = []
    if label_files_dict:
        logger.info(label_files_dict)
        data_folder = os.path.join(selected_project.dir_name, "data")
        label_thumbnail_folder = os.path.join(selected_project.dir_name, "label_thumbnails")

        for project_folder, label_files in label_files_dict.items():
            for task_idx, label_file in enumerate(label_files):
                st.write(f"Analyzing class labels for task {task_idx}")
                logger.info(os.path.join(project_folder, label_file))
                data_labels = DataLabels.load(os.path.join(project_folder, label_file))
                thumbnails, names = generate_label_thumbnails(data_folder, data_labels, label_thumbnail_folder)

                if thumbnails:
                    label_thumbnails.extend(thumbnails)
                    thumbnail_names.extend(names)

                cur_class_labels = data_labels.get_class_labels()
                class_labels = class_labels.union(cur_class_labels)

        class_count = len(class_labels)
        st.write(f"Found {len(label_thumbnails)} labels in {class_count} classes: {class_labels}")
        cluster_labels = cluster_images(label_thumbnails, n_clusters=class_count)
        reduced_features = reduce_features(label_thumbnails)

        plot_image_clusters(selected_project.id, "label clusters", thumbnail_names,
                            label_thumbnails, cluster_labels, reduced_features)


def auto_review():
    selected_project = select_project(is_sidebar=True)

    with st.form("Auto-Reviews"):
        options = [OVERLAPS, TINY_OBJECTS, CLUSTER_LABELS]
        selected_options = []
        if selected_project:
            for option in options:
                selected = st.checkbox(option)
                if selected:
                    selected_options.append(selected)

            if CLUSTER_LABELS in selected_options:
                st.write(selected_options)

            start = st.form_submit_button("Start auto-review")
            if start:
                st.write("Starting")
                detect_label_anomalies(selected_project)


def main():
    # Clear the sidebar
    st.sidebar.empty()
    # Clear the main page
    st.empty()

    menu = {
        "Review Images": lambda: review_images(),
        "Review Task": lambda: review_task(),
        "Compare Tasks": lambda: compare_tasks(),
        "Auto Review": lambda: auto_review()
    }

    # Create a sidebar with menu options
    selected_action = st.sidebar.radio("Choose action", list(menu.keys()))

    if selected_action:
        # Call the selected method based on the user's selection
        menu[selected_action]()


if __name__ == '__main__':
    if not is_authenticated():
        login()
    else:
        main()
        logout()
