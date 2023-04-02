import tempfile

import altair as alt
import attr
import streamlit as st

from projects_info import ProjectsInfo


@attr.s(slots=True, frozen=False)
class SessionState:
    projects_info = attr.ib(default=None, validator=attr.validators.instance_of(ProjectsInfo))
    charts = attr.ib(default=[])
    tasks_info = attr.ib(default=None)
    users = attr.ib(default=None)

    def display_chart(self, chart):
        st.altair_chart(chart, use_container_width=True)
        self.charts.append(chart)

    # Create a function to save all charts in the SessionState object
    def show_download_charts_button(self):
        combined_chart = alt.concat(*self.charts, columns=len(self.charts))
        # Create a temporary file
        combined_file = tempfile.NamedTemporaryFile(suffix='.html', delete=False)
        # # Save chart as HTML file
        combined_chart.save(combined_file.name, format='html')

        # Add download button
        with open(combined_file.name, 'rb') as f:
            file_bytes = f.read()
            st.download_button(
                label='Download combined chart',
                data=file_bytes,
                file_name=combined_file.name,
                mime='text/html'
            )
