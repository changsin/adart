import os.path

import altair as alt
import attr
import streamlit as st

from projects_info import ProjectsInfo

ADQ_WORKING_FOLDER = ".adq"
PROJECTS = "projects"
TASKS = "tasks"
JSON_EXT = ".json"

CVAT_XML = "CVAT XML"
PASCAL_VOC_XML = "PASCAL VOC XML"
COCO_JSON = "COCO JSON"
ADQ_JSON = "ADQ JSON"

SUPPORTED_FORMATS = [CVAT_XML, PASCAL_VOC_XML, COCO_JSON, ADQ_JSON]
SUPPORTED_IMAGE_FILE_EXTENSIONS = ["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.tiff", "*.gif"]

PROJECT_COLUMNS = ['id', 'name', 'file_format_id',
                   'total_count', 'task_total_count', 'task_done_count']

TASK_COLUMNS = ['id', 'name', "project_id"]


@attr.s(slots=True, frozen=False)
class SessionState:
    projects_info = attr.ib(default=None, validator=attr.validators.instance_of(ProjectsInfo))
    charts = attr.ib(default=dict())
    tasks_info = attr.ib(default=None)
    users = attr.ib(default=None)

    def display_chart(self, project_id, name, chart):
        st.altair_chart(chart, use_container_width=True)
        if self.charts.get(project_id):
            self.charts[project_id][name] = chart
        else:
            self.charts.setdefault(project_id, {})[name] = chart

    # Create a function to save all charts in the SessionState object
    def show_download_charts_button(self, project_id):
        if not self.charts.get(project_id):
            st.text("Nothing here")
            return

        combined_chart = alt.concat(*self.charts[project_id].values(), columns=len(self.charts[project_id]))
        # Create a temporary file
        combined_filename = "{}.{}.{}".format(project_id, "combined_charts", "html")
        full_path = os.path.join(ADQ_WORKING_FOLDER, project_id, combined_filename)
        # # Save chart as HTML file
        combined_chart.save(full_path, format='html')

        download_disabled = True
        if os.path.exists(full_path):
            download_disabled = False

        # Add download button
        with open(full_path, 'rb') as f:
            file_bytes = f.read()
            st.download_button(
                label='Download combined chart',
                data=file_bytes,
                file_name=combined_filename,
                mime='text/html',
                disabled=download_disabled
            )
