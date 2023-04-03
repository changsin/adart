import tempfile

import altair as alt
import attr
import streamlit as st

from projects_info import ProjectsInfo


@attr.s(slots=True, frozen=False)
class SessionState:
    projects_info = attr.ib(default=None, validator=attr.validators.instance_of(ProjectsInfo))
    charts = attr.ib(default=dict())
    tasks_info = attr.ib(default=None)
    users = attr.ib(default=None)

    def display_chart(self, name, chart):
        st.altair_chart(chart, use_container_width=True)
        self.charts[name] = chart

    # Create a function to save all charts in the SessionState object
    def show_download_charts_button(self, project_id):
        combined_chart = alt.concat(*self.charts.values(), columns=len(self.charts))
        # Create a temporary file
        combined_filename = "{}.{}.{}".format(project_id, "combined_charts", "html")
        # # Save chart as HTML file
        combined_chart.save(combined_filename, format='html')

        # Add download button
        with open(combined_filename, 'rb') as f:
            file_bytes = f.read()
            st.download_button(
                label='Download combined chart',
                data=file_bytes,
                file_name=combined_filename,
                mime='text/html'
            )
