import datetime
import json
import shutil

from st_aggrid import AgGrid

from charts import *
from convert_lib import convert_CVAT_to_Form
from label_quality import *
from projects_info import ProjectsInfo, Project
from review_images import show_images
from constants import *


def default(obj):
    if hasattr(obj, 'to_json'):
        return obj.to_json()
    raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')


def home():
    st.write("DaRT")


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
                                     default=default, indent=2),
                          ADQ_WORKING_FOLDER,
                          PROJECTS + JSON_EXT)

            dashboard()


def create_tasks():
    with st.form("Create Tasks"):
        sample_percent = st.text_input("% of samples")

        st.form_submit_button("Create tasks")


def delete_project():
    selected_project = _select_project()

    if selected_project:
        if st.button("Are you sure you want to delete the project {}-{}?"
                     .format(selected_project.id, selected_project.name)):
            # Your code to handle the user choosing not to proceed
            projects_info = st.session_state[PROJECTS]
            projects_info.projects.remove(selected_project)

            folder_path = os.path.join(ADQ_WORKING_FOLDER, str(selected_project.id))
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)
            st.markdown("**Deleted project {}-{}".format(selected_project.id, selected_project.name))

            utils.to_file(json.dumps(projects_info,
                                     default=default, indent=2),
                          ADQ_WORKING_FOLDER,
                          PROJECTS + JSON_EXT)

            # TODO: Delete tasks too
            dashboard()


def show_file_info():
    selected_project = _select_project()

    if selected_project:
        if selected_project.image_files:
            st.markdown("# Image Files Info")
            chart_images_ctime = plot_datetime("### Created date time", selected_project.image_files)
            if chart_images_ctime:
                display_chart(selected_project.id, "image_files_ctime", chart_images_ctime)

            chart_images_file_sizes = plot_file_sizes("### File size", selected_project.image_files)
            if chart_images_file_sizes:
                display_chart(selected_project.id, "image_file_sizes", chart_images_file_sizes)

        if selected_project.label_files:
            st.markdown("# Label Files Info")
            chart_labels_ctime = plot_datetime("### Created date time", selected_project.label_files)
            if chart_labels_ctime:
                display_chart(selected_project.id, "label_files_ctime", chart_labels_ctime)

            chart_label_file_sizes = plot_file_sizes("### File size", selected_project.label_files)
            if chart_label_file_sizes:
                display_chart(selected_project.id, "label_file_sizes", chart_label_file_sizes)

        show_download_charts_button(selected_project.id)


def show_image_quality():
    selected_project = _select_project()

    if selected_project:
        chart_aspect_ratios, chart_brightness = plot_aspect_ratios_brightness("### Aspect ratios",
                                                                              selected_project.image_files)
        # Display the histogram in Streamlit
        if chart_aspect_ratios:
            display_chart(selected_project.id, "aspect_ratios", chart_aspect_ratios)
        if chart_brightness:
            display_chart(selected_project.id, "brightness", chart_brightness)

        show_download_charts_button(selected_project.id)


def _select_project():
    projects_info = st.session_state[PROJECTS]
    if projects_info.num_count > 0:
        df_projects = pd.DataFrame(projects_info.to_json()[PROJECTS])
        df_project_id_names = df_projects[["id", "name"]]
        options = ["{}-{}".format(project_id, name)
                   for project_id, name in df_project_id_names[["id", "name"]].values.tolist()]
        # set an empty string as the default selection - no action
        options.append("")
        selected_project = st.selectbox("Select project",
                                        options=options,
                                        index=len(options) - 1)
        if selected_project:
            project_id, name, = selected_project.split('-', maxsplit=1)
            return projects_info.get_project_by_id(int(project_id))
    else:
        st.markdown("**No project is created!**")


def show_label_quality():
    selected_project = _select_project()
    if selected_project:
        if not selected_project.label_files:
            st.write("No labels!")
            return

        class_labels, overlap_areas, dimensions = load_label_files("Label quality", selected_project.label_files)

        chart_class_count = plot_chart("Class Count", "class", "count", class_labels)
        if chart_class_count:
            display_chart(selected_project.id, "class_count", chart_class_count)

        chart_overlap_areas = plot_chart("Overlap Areas",
                                         x_label="overlap %", y_label="count",
                                         data_dict=overlap_areas)
        if chart_overlap_areas:
            display_chart(selected_project.id, "overlap_areas", chart_overlap_areas)

        # create DataFrame from dictionary
        df_dimensions = pd.DataFrame.from_dict(dimensions, orient='index', columns=['width', 'height'])

        # apply function to split pairs into dictionary
        dimension_dict = dict(zip(df_dimensions['width'], df_dimensions['height']))

        # widths, heights = zip(*df_dimensions.apply(lambda x: tuple(x)))
        # df_dimensions = pd.concat([pd.Series(widths), pd.Series(heights)], axis=1)
        chart_dimensions = plot_chart("Dimensions",
                                      x_label="width", y_label="height",
                                      data_dict=dimension_dict, chart_type="circle")
        if chart_dimensions:
            display_chart(selected_project.id, "dimensions", chart_dimensions)


def review_images():
    selected_project = _select_project()
    if selected_project:
        show_images(selected_project.image_files)


def start_st():
    if not os.path.exists(ADQ_WORKING_FOLDER):
        os.mkdir(ADQ_WORKING_FOLDER)

    st.sidebar.header("**DaRT** - Data Reviewing Tool")

    json_projects = utils.from_file("{\"num_count\":0,\"projects\":[]}",
                                    # os.path.join(os.getcwd(), "data"),
                                    ADQ_WORKING_FOLDER,
                                    PROJECTS + JSON_EXT)
    projects_info = ProjectsInfo.from_json(json_projects)

    st.session_state[PROJECTS] = projects_info
    # session_state = SessionState(projects_info=projects_info)

    menu = {
        "Home": lambda: home(),
        "Dashboard": lambda: dashboard(),
        "Create Projects": lambda: create_projects(),
        "Create Tasks": lambda: create_tasks(),
        "Delete Project": lambda: delete_project(),
        "Show file info": lambda: show_file_info(),
        "Show image quality": lambda: show_image_quality(),
        "Show label quality": lambda: show_label_quality(),
        "Review images": lambda: review_images()
    }

    # Create a sidebar with menu options
    selected_action = st.sidebar.radio("Choose action", list(menu.keys()))

    if selected_action:
        # Call the selected method based on the user's selection
        menu[selected_action]()


if __name__ == '__main__':
    # dashboard()
    start_st()

