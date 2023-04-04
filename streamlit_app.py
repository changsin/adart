import json
import shutil

from constants import *
from pages.create_projects import create_projects
from pages.dashboard import dashboard
from pages.label_quality import *
from pages.review_images import show_images
from models.projects_info import ProjectsInfo


def home():
    st.write("DaRT")


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
                                     default=utils.default, indent=2),
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

        chart_label_quality(selected_project)


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

