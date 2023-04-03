import datetime
import json
import shutil

from st_aggrid import AgGrid

from charts import *
from convert_lib import convert_CVAT_to_Form
from label_quality import *
from projects_info import Project
from review_images import show_images
from session_state import *


def default(obj):
    if hasattr(obj, 'to_json'):
        return obj.to_json()
    raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')


def home(menu_dart: SessionState):
    st.write("DaRT")


def dashboard(menu_dart: SessionState):
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
    if menu_dart.projects_info.num_count > 0:
        # turn a class object to json dictionary to be processed by pandas dataframe
        df_projects = pd.DataFrame(menu_dart.projects_info.projects)
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


def create_projects(menu_dart: SessionState):
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
            st.markdown(f"**Name:** {name}")
            st.markdown(f"**Images folder:** {images_folder}")
            # get_folder_info(images_folder, SUPPORTED_IMAGE_FILE_EXTENSIONS)
            # show_dir_tree(Path(images_folder))
            # files_tree = generate_file_tree(images_folder)
            # display_file_tree(files_tree, indent=2)
            image_files = utils.generate_file_tree(images_folder, images_format_type.split())

            st.markdown(f"**Labels folder:** {labels_folder}")
            patterns = ["*.xml"]
            if labels_format_type.endswith("JSON"):
                patterns = ["*.json"]

            label_files = utils.generate_file_tree(labels_folder, patterns)

            project_id = menu_dart.projects_info.get_next_project_id()

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
            menu_dart.projects_info.add(new_project.to_json())

            utils.to_file(json.dumps(menu_dart.projects_info,
                                     default=default, indent=2),
                          ADQ_WORKING_FOLDER,
                          PROJECTS + JSON_EXT)

            dashboard(menu_dart)


def create_tasks(menu_dart: SessionState):
    with st.form("Create Tasks"):
        sample_percent = st.text_input("% of samples")

        st.form_submit_button("Create tasks")


def show_file_info(session_state: SessionState):
    selected_project = _select_project(session_state)

    if selected_project and len(selected_project) > 0:
        project_id, name, = selected_project.split('-', maxsplit=1)
        project_selected = session_state.projects_info.get_project_by_id(int(project_id))

        if project_selected.get("image_files"):
            st.markdown("# Image Files Info")
            chart_images_ctime = plot_datetime("### Created date time", project_selected["image_files"])
            if chart_images_ctime:
                session_state.display_chart(project_id, "image_files_ctime", chart_images_ctime)

            chart_images_file_sizes = plot_file_sizes("### File size", project_selected["image_files"])
            if chart_images_file_sizes:
                session_state.display_chart(project_id, "image_file_sizes", chart_images_file_sizes)

        if project_selected.get("label_files"):
            st.markdown("# Label Files Info")
            chart_labels_ctime = plot_datetime("### Created date time", project_selected["label_files"])
            if chart_labels_ctime:
                session_state.display_chart(project_id, "label_files_ctime", chart_labels_ctime)

            chart_label_file_sizes = plot_file_sizes("### File size", project_selected["label_files"])
            if chart_label_file_sizes:
                session_state.display_chart(project_id, "label_file_sizes", chart_label_file_sizes)

        session_state.show_download_charts_button(project_id)


def show_image_quality(session_state: SessionState):
    selected_project = _select_project(session_state)

    if selected_project and len(selected_project) > 0:
        project_id, name = selected_project.split('-', maxsplit=1)
        project_selected = session_state.projects_info.get_project_by_id(int(project_id))
        chart_aspect_ratios, chart_brightness = plot_aspect_ratios_brightness("### Aspect ratios",
                                                                              project_selected["image_files"])
        # Display the histogram in Streamlit
        if chart_aspect_ratios:
            session_state.display_chart(project_id, "aspect_ratios", chart_aspect_ratios)
        if chart_brightness:
            session_state.display_chart(project_id, "brightness", chart_brightness)

        session_state.show_download_charts_button(project_id)


def _select_project(session_state: SessionState):
    if session_state.projects_info.num_count > 0:
        df_projects = pd.DataFrame(session_state.projects_info.projects)
        df_project_id_names = df_projects[["id", "name"]]
        options = ["{}-{}".format(project_id, name)
                   for project_id, name in df_project_id_names[["id", "name"]].values.tolist()]
        # set an empty string as the default selection - no action
        options.append("")
        return st.selectbox("Select project",
                            options=options,
                            index=len(options) - 1)
    else:
        st.markdown("**No project is created!**")


def show_label_quality(session_state: SessionState):
    selected_project = _select_project(session_state)
    if selected_project and len(selected_project) > 0:
        project_id, name = selected_project.split('-', maxsplit=1)
        project_selected = session_state.projects_info.get_project_by_id(int(project_id))
        class_labels, overlap_areas, dimensions = load_label_files("Label quality", project_selected["label_files"])

        chart_class_count = plot_chart("Class Count", "class", "count", class_labels)
        if chart_class_count:
            session_state.display_chart(project_id, "class_count", chart_class_count)

        chart_overlap_areas = plot_chart("Overlap Areas",
                                         x_label="overlap %", y_label="count",
                                         data_dict=overlap_areas)
        if chart_overlap_areas:
            session_state.display_chart(project_id, "overlap_areas", chart_overlap_areas)

        # create DataFrame from dictionary
        df_dimensions = pd.DataFrame.from_dict(dimensions, orient='index', columns=['width', 'height'])

        # apply function to split pairs into dictionary
        dimension_dict = dict(zip(df_dimensions['width'], df_dimensions['height']))
        print(dimension_dict)

        # widths, heights = zip(*df_dimensions.apply(lambda x: tuple(x)))
        # df_dimensions = pd.concat([pd.Series(widths), pd.Series(heights)], axis=1)
        chart_dimensions = plot_chart("Dimensions",
                                      x_label="width", y_label="height",
                                      data_dict=dimension_dict, chart_type="circle")
        if chart_dimensions:
            session_state.display_chart(project_id, "dimensions", chart_dimensions)


def review_images(session_state: SessionState):
    selected_project = _select_project(session_state)
    if selected_project and len(selected_project) > 0:
        project_id, name = selected_project.split('-', maxsplit=1)
        project_selected = session_state.projects_info.get_project_by_id(int(project_id))

        show_images(project_selected["image_files"])


def start_st():
    if not os.path.exists(ADQ_WORKING_FOLDER):
        os.mkdir(ADQ_WORKING_FOLDER)

    st.sidebar.header("**DaRT** - Data Reviewing Tool")

    json_projects = utils.from_file("{\"num_count\":0,\"projects\":[]}",
                                    # os.path.join(os.getcwd(), "data"),
                                    ADQ_WORKING_FOLDER,
                                    PROJECTS + JSON_EXT)
    projects_info = ProjectsInfo.from_json(json_projects)

    session_state = SessionState(projects_info=projects_info)

    menu = {
        "Home": lambda: home(session_state),
        "Dashboard": lambda: dashboard(session_state),
        "Create Projects": lambda: create_projects(session_state),
        "Create Tasks": lambda: create_tasks(session_state),
        "Show file info": lambda: show_file_info(session_state),
        "Show image quality": lambda: show_image_quality(session_state),
        "Show label quality": lambda: show_label_quality(session_state),
        "Review images": lambda: review_images(session_state)
    }

    # Create a sidebar with menu options
    selected_action = st.sidebar.radio("Choose action", list(menu.keys()))

    if selected_action:
        # Call the selected method based on the user's selection
        menu[selected_action]()


if __name__ == '__main__':
    # dashboard()
    start_st()

