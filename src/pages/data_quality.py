import importlib.util

spec = importlib.util.find_spec("src")
if spec is None:
    import sys
    from pathlib import Path

    path_root = Path(__file__).parents[2]
    sys.path.append(str(path_root))

from src.common.charts import *
from src.home import select_project


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

    if selected_project and selected_project.image_files:
        chart_aspect_ratios, chart_brightness = plot_aspect_ratios_brightness("### Aspect ratios",
                                                                              selected_project.image_files)
        # Display the histogram in Streamlit
        if chart_aspect_ratios:
            display_chart(selected_project.id, "aspect_ratios", chart_aspect_ratios)
        if chart_brightness:
            display_chart(selected_project.id, "brightness", chart_brightness)

        show_download_charts_button(selected_project.id)
    else:
        st.write("No image data")


def main():
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
