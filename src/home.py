import sys
from pathlib import Path

path_root = Path(__file__).parents[1]
sys.path.append(str(path_root))

from src.common.charts import *
from src.common import utils
from src.models.projects_info import ProjectsInfo


def get_projects_info():
    if st.session_state.get(constants.PROJECTS):
        return st.session_state[constants.PROJECTS]

    json_projects = utils.from_file("{\"num_count\":0,\"projects\":[]}",
                                    # os.path.join(os.getcwd(), "data"),
                                    constants.ADQ_WORKING_FOLDER,
                                    constants.PROJECTS + constants.JSON_EXT)
    return ProjectsInfo.from_json(json_projects)


def select_project():
    projects_info = get_projects_info()
    if projects_info.num_count > 0:
        df_projects = pd.DataFrame(projects_info.to_json()[constants.PROJECTS])
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
            print(" selected {}-{}".format(project_id, name))
            return projects_info.get_project_by_id(int(project_id))
    else:
        st.markdown("**No project is created!**")


def create_tasks():
    with st.form("Create Tasks"):
        sample_percent = st.text_input("% of samples")

        st.form_submit_button("Create tasks")


def show_file_info():
    selected_project = select_project()

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
    selected_project = select_project()

    if selected_project:
        chart_aspect_ratios, chart_brightness = plot_aspect_ratios_brightness("### Aspect ratios",
                                                                              selected_project.image_files)
        # Display the histogram in Streamlit
        if chart_aspect_ratios:
            display_chart(selected_project.id, "aspect_ratios", chart_aspect_ratios)
        if chart_brightness:
            display_chart(selected_project.id, "brightness", chart_brightness)

        show_download_charts_button(selected_project.id)


def main():
    if not os.path.exists(constants.ADQ_WORKING_FOLDER):
        os.mkdir(constants.ADQ_WORKING_FOLDER)

    st.set_page_config(page_title="DaRT")
    st.sidebar.header("**DaRT** - Data Reviewing Tool")

    json_projects = utils.from_file("{\"num_count\":0,\"projects\":[]}",
                                    # os.path.join(os.getcwd(), "data"),
                                    constants.ADQ_WORKING_FOLDER,
                                    constants.PROJECTS + constants.JSON_EXT)
    projects_info = ProjectsInfo.from_json(json_projects)

    st.session_state[constants.PROJECTS] = projects_info

    menu = {
        "Show file info": lambda: show_file_info(),
        "Show image quality": lambda: show_image_quality(),
    }

    # Create a sidebar with menu options
    selected_action = st.sidebar.radio("Choose action", list(menu.keys()))

    if selected_action:
        # Call the selected method based on the user's selection
        menu[selected_action]()


if __name__ == '__main__':
    main()
