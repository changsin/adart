import json
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
    def download_charts(self):
        images = []
        chart_filenames = []
        for i, chart in enumerate(self.charts):
            # Create a temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
            # Wait for 2 seconds before saving the chart
            # time.sleep(2)
            print("saving into {}".format(temp_file.name))
            # this doesn't work for me
            # altair_saver.save(chart, temp_file.name, format='HTML')
            json_chart = chart.to_json()
            with open(temp_file.name, 'w') as f:
                json.dump(json_chart, f)

            # # Open image files using cv2
            # image = cv2.imread(temp_file.name)
            # images.append(image)
            chart_filenames.append(temp_file.name)

        # # Combine images vertically
        # combined_image = cv2.vconcat(images)
        #
        # # Create a temporary file
        # combined_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        # # Save combined image file
        # cv2.imwrite(combined_file.name, combined_image)
        #
        # # Display combined image in Streamlit app
        # st.image(combined_file.name)

        # Load the saved charts and concatenate them in a loop
        combined_chart = None
        for filename in chart_filenames:
            with open(filename, 'r') as f:
                chart_dict = json.load(f)
            chart = alt.Chart.from_dict(chart_dict)
            if combined_chart is None:
                combined_chart = chart
            else:
                combined_chart &= chart

        # with open(chart_filenames[0], 'rb') as f:
        #     data = f.read()
        #     b64 = base64.b64encode(data).decode('UTF-8')
        #     href = f'<a href="data:file/png;base64,{b64}" download="{chart_filenames[0]}">Download file</a>'
        #     return href
