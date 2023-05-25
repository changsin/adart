import datetime as dt
import os

import altair as alt
import cv2
import pandas as pd
import streamlit as st

from src.common import constants, utils

import plotly.graph_objects as go
import plotly.express as px
import plotly.offline as pyo
import plotly.io as pio
import plotly.subplots as sp
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

@st.cache_data
def plot_aspect_ratios_brightness(title: str, files_dict: dict):
    if files_dict is None or len(files_dict.items()) == 0:
        return

    # Initialize a list to store the aspect ratios
    aspect_ratios = {}
    brightness_values = {}

    # Loop through all the files in the folder and calculate their aspect ratios
    for folder, files in files_dict.items():
        for file in files:
            image_path = os.path.join(folder, file)
            # Read the image using opencv-python
            img = cv2.imread(image_path)

            if img is None:
                continue

            # Get the width and height of the image
            height, width, _ = img.shape

            # Calculate the aspect ratio
            aspect_ratio = width / height
            if aspect_ratios.get(aspect_ratio):
                aspect_ratios[aspect_ratio] = aspect_ratios[aspect_ratio] + 1
            else:
                aspect_ratios[aspect_ratio] = 1

            # Convert the image to grayscale
            gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # Calculate the average brightness of the image
            brightness = gray_img.mean()
            if brightness_values.get(brightness):
                brightness_values[brightness] = brightness_values[brightness] + 1
            else:
                brightness_values[brightness] = 1

    aspect_ratios_list = [(k, v) for k, v in aspect_ratios.items()]

    # Done with the help of ChatGPT:
    # Create a Pandas DataFrame from the aspect ratios
    # Passing the keys and values of the dictionary directly to the Pandas DataFrame results in a problem.
    # It is possible that the values are being coerced to a non-numeric data type,
    # which could cause issues with the count() aggregation function.
    #
    # To resolve this issue, you can try converting the aspect_ratios dictionary into a list of tuples,
    # where each tuple contains the aspect ratio value and the count of images with that aspect ratio.
    # You can then pass this list to the Pandas DataFrame.
    df_aspect_ratios = pd.DataFrame(aspect_ratios_list, columns=['aspect_ratio', 'count'])

    # # Create a histogram of the aspect ratios using Altair
    # chart_aspect_ratios = alt.Chart(df_aspect_ratios).mark_bar().encode(
    #     x=alt.X('aspect_ratio'),
    #     y=alt.Y('count:Q', title='Count'),
    #     tooltip=['aspect_ratio', 'count:Q']
    # ).properties(
    #     title='Aspect Ratios of Images'
    # )
    # chart_aspect_ratios = chart_aspect_ratios.interactive()  # make the chart interactive
    # chart_aspect_ratios = chart_aspect_ratios.properties(
    #     width=600,
    #     height=400
    # ).add_selection(
    #     alt.selection_interval(bind='scales', encodings=['x', 'y'])
    # ).add_selection(
    #     alt.selection(type='interval', bind='scales', encodings=['x', 'y'])
    # )

    # Create a histogram of the aspect ratios using Plotly
    fig_aspect_ratios = go.Figure(data=[go.Bar(x=df_aspect_ratios['aspect_ratio'], y=df_aspect_ratios['count'])])

    fig_aspect_ratios.update_layout(
        title='Aspect Ratios of Images',
        xaxis_title='Aspect Ratio',
        yaxis_title='Count',
        width=600,
        height=400,
        bargap=0.1
    )

    # Make the chart interactive
    fig_aspect_ratios.update_xaxes(rangeselector=dict(buttons=list([
        dict(count=1, label="1m", step="month", stepmode="backward"),
        dict(count=6, label="6m", step="month", stepmode="backward"),
        dict(count=1, label="YTD", step="year", stepmode="todate"),
        dict(count=1, label="1y", step="year", stepmode="backward"),
        dict(step="all")
    ])), rangeslider=dict(visible=True))

    # Display the plotly chart
    st.plotly_chart(fig_aspect_ratios)

    brightness_values_list = [(k, v) for k, v in brightness_values.items()]
    # Create a Pandas DataFrame from the brightness
    df_brightness = pd.DataFrame(brightness_values_list, columns=['brightness', 'count'])

    # # Create a histogram of the brightness using Altair
    # chart_brightness = alt.Chart(df_brightness).mark_bar().encode(
    #     x=alt.X('brightness', bin=alt.Bin(step=10)),
    #     y=alt.Y('count:Q', title='Count'),
    #     tooltip=['brightness', 'count:Q']
    # ).properties(
    #     title='Brightness of Images'
    # )
    # chart_brightness = chart_brightness.interactive()  # make the chart interactive
    # chart_brightness = chart_brightness.properties(
    #     width=600,
    #     height=400
    # ).add_selection(
    #     alt.selection_interval(bind='scales', encodings=['x', 'y'])
    # ).add_selection(
    #     alt.selection(type='interval', bind='scales', encodings=['x', 'y'])
    # )

    chart_brightness = px.histogram(df_brightness, x='brightness', nbins=50,
                                    title='Brightness of Images',
                                    labels={'brightness': 'Brightness', 'count': 'Count'},
                                    hover_data=['brightness', 'count'])
    
    chart_brightness.update_xaxes(rangeselector=dict(buttons=list([
        dict(count=1, label="1m", step="month", stepmode="backward"),
        dict(count=6, label="6m", step="month", stepmode="backward"),
        dict(count=1, label="YTD", step="year", stepmode="todate"),
        dict(count=1, label="1y", step="year", stepmode="backward"),
        dict(step="all")
    ])), rangeslider=dict(visible=True))

    # Display the plot
    st.plotly_chart(chart_brightness)

    return fig_aspect_ratios, chart_brightness


@st.cache_data
def plot_file_sizes(df_file_info: pd.DataFrame):
    df_file_info['size'] = df_file_info['size'].astype(int)

    # # Create a histogram using Altair
    # chart = alt.Chart(df_file_info).mark_bar().encode(
    #     alt.X('size', bin=alt.Bin(maxbins=50), title='File Size (bytes)'),
    #     y='count()',
    #     # tooltip=['count()', alt.datum.file_size, 'file']
    # ).properties(
    #     title='File Size Distribution'
    # )
    #
    # chart = chart.interactive()  # make the chart interactive
    # chart = chart.properties(
    #     width=600,
    #     height=400
    # ).add_selection(
    #     alt.selection_interval(bind='scales', encodings=['x', 'y'])
    # ).add_selection(
    #     alt.selection(type='interval', bind='scales', encodings=['x', 'y'])
    # )
    #
    # return chart

    #Redoing the chart using plotly
    fig = px.histogram(df_file_info, x='size', nbins=50,
                       title='File Size Distribution',
                       labels={'size': 'File Size (bytes)', 'count': 'Count'},
                       hover_data=['size'])

    fig.update_layout(width=600, height=400, hovermode='closest')

    # Display the plot
    st.plotly_chart(fig)


@st.cache_data
def plot_file_info(title: str, files_dict: dict):
    if files_dict is None or len(files_dict.items()) == 0:
        return

    st.header(title)
    file_info_dict = dict()
    for folder, files in files_dict.items():
        level = folder.count(os.sep)
        indent = '-' * level
        # st.markdown('{}📁({}) {}/'.format(indent, len(files), folder))
        with st.expander('📁({}) {}/'.format(len(files), folder.replace(constants.ADQ_WORKING_FOLDER, ""))):
            for file in files:
                file_stat = os.stat(os.path.join(folder, file))
                dt_cdatetime = dt.datetime.fromtimestamp(file_stat.st_ctime)
                st.markdown("📄{} ({}) created: {}".format(file,
                                                           utils.humanize_bytes(file_stat.st_size),
                                                           dt_cdatetime.date()))
                # st.markdown("📄{} ({}) {}".format(file,
                #                                  utils.humanize_bytes(file_stat.st_size),
                #                                  dt_cdatetime.date()))
                ctime_object = dt_cdatetime.time()
                # Append date and time to x and y data lists
                file_info_dict[file] = (dt_cdatetime.date(), float(ctime_object.strftime('%H.%M')), file_stat.st_size)

    df_ctime = pd.DataFrame.from_dict(file_info_dict, orient='index', columns=['date', 'time', 'size'])
    df_ctime = df_ctime.assign(file=file_info_dict.keys())
    # df_ctime = df_ctime.assign(file=file_info_dict.keys(), modified=[t[0] for t in file_info_dict.values()])

    # convert the date column to a string representation
    df_ctime['date'] = df_ctime['date'].astype(str)

    # chart_ctime = alt.Chart(df_ctime).mark_circle().encode(
    #     x='date',
    #     y='time',
    #     tooltip=['date', 'time', 'size', 'file'],
    # ).properties(
    #         title="Created Time"
    #     )
    #
    # # make the chart interactive
    # chart_ctime = chart_ctime.interactive()
    # chart_ctime = chart_ctime.properties(
    #     width=600,
    #     height=400
    # ).add_selection(
    #     alt.selection_interval(bind='scales', encodings=['x', 'y'])
    # ).add_selection(
    #     alt.selection(type='interval', bind='scales', encodings=['x', 'y'])
    # )

    #Redo with Plotly
    chart_ctime = px.scatter(df_ctime, x='date', y='time',
                             hover_data=['date', 'time', 'size', 'file'],
                             title='Created Time')

    chart_ctime.update_layout(width=600, height=400, hovermode='closest')

    # Display the plot
    st.plotly_chart(chart_ctime)

    chart_sizes = plot_file_sizes(df_ctime)

    return chart_ctime, chart_sizes


@st.cache_data
def plot_chart(title: str, x_label: str, y_label: str, data_dict: dict, chart_type="bar"):
    if data_dict is None or len(data_dict.items()) == 0:
        return

    data = pd.DataFrame({
        x_label: data_dict.keys(),
        y_label: data_dict.values()
    })

    # # Create a dropdown menu for the user to select which items to display
    # selection = alt.selection_multi(fields=[x_label], bind='legend')
    #
    # # Create a histogram using Altair
    # if chart_type == "circle":
    #     # Convert the date field to a datetime format
    #     # data[x_label] = pd.to_datetime(data[x_label])
    #     chart = alt.Chart(data).mark_circle(size=200).encode(
    #         x=alt.X(x_label),
    #         y=alt.Y(y_label),
    #         tooltip=[x_label, y_label],
    #         color=alt.Color(x_label, legend=alt.Legend(title=x_label))
    #     ).properties(
    #         title=title
    #     )
    # elif chart_type == "line":
    #     chart = alt.Chart(data).mark_line().encode(
    #         x=alt.X(x_label),
    #         y=alt.Y(y_label),
    #         tooltip=[x_label, y_label],
    #         color=alt.Color(x_label, legend=alt.Legend(title=x_label))
    #     ).properties(
    #         title=title
    #     )
    # else:
    #     chart = alt.Chart(data).mark_bar().encode(
    #         x=alt.X(x_label),
    #         y=alt.Y(y_label),
    #         tooltip=[x_label, y_label],
    #         color=alt.Color(x_label, legend=alt.Legend(title=x_label))
    #     ).properties(
    #         title=title
    #     )
    #
    # # make the chart interactive
    # chart = chart.interactive()
    # chart = chart.properties(
    #     width=600,
    #     height=400
    # ).add_selection(
    #     alt.selection_interval(bind='scales', encodings=['x', 'y'])
    # ).add_selection(
    #     alt.selection(type='interval', bind='scales', encodings=['x', 'y'])
    # ).add_selection(selection)
    #
    # return chart

    # Plotly
    # Create a dropdown menu for the user to select which items to display
    selection = []

    # Create a scatter plot using Plotly
    if chart_type == "circle":
        chart = px.scatter(data_frame=data, x=x_label, y=y_label, color=x_label,
                           hover_data=[x_label, y_label], title=title)
    elif chart_type == "line":
        chart = px.line(data_frame=data, x=x_label, y=y_label, color=x_label,
                        hover_data=[x_label, y_label], title=title)
    else:
        chart = px.bar(data_frame=data, x=x_label, y=y_label, color=x_label,
                       hover_data=[x_label, y_label], title=title)

    # Configure the layout
    chart.update_layout(width=600, height=400, hovermode='closest')

    # Add selection interaction
    for field in selection:
        chart.data[0].update({field: True})

    # Display the plot
    st.plotly_chart(chart)


# def display_chart(project_id, name, chart, column=None):
#     if column:
#         column.altair_chart(chart, use_container_width=True)
#     else:
#         st.altair_chart(chart, use_container_width=True)

def display_chart(project_id, name, chart, column=None):
    if column:
        column.plotly_chart(chart, use_container_width=True)
    else:
        st.plotly_chart(chart, use_container_width=True)

    # save to the session_state for later use
    charts = dict()
    if st.session_state.get(constants.CHARTS):
        charts = st.session_state[constants.CHARTS]
    else:
        st.session_state[constants.CHARTS] = charts

    if charts.get(project_id):
        charts[project_id][name] = chart
    else:
        charts.setdefault(project_id, {})[name] = chart


# Create a function to save all charts in the SessionState object
def show_download_charts_button(project_id):
    if not st.session_state.get(constants.CHARTS):
        st.text("No chart was saved")
        return

    charts = st.session_state[constants.CHARTS]
    if not charts.get(project_id):
        st.text("Nothing here")
        return

    # combined_chart = alt.concat(*charts[project_id].values(), columns=len(charts[project_id]))
    # # Create a temporary file
    # combined_filename = "{}.{}.{}".format(project_id, "combined_charts", "html")
    # full_path = os.path.join(constants.ADQ_WORKING_FOLDER, str(project_id), combined_filename)
    # # # Save chart as HTML file
    # combined_chart.save(full_path, format='html')
    #
    # download_disabled = True
    # if os.path.exists(full_path):
    #     download_disabled = False
    #
    # # Add download button
    # with open(full_path, 'rb') as f:
    #     file_bytes = f.read()
    #     st.download_button(
    #         label='Download combined chart',
    #         data=file_bytes,
    #         file_name=combined_filename,
    #         mime='text/html',
    #         disabled=download_disabled
    #     )

    charts_list = [*charts[project_id].values()]

    # Create a temporary file
    combined_filename = f"{project_id}.combined_charts.pdf"
    full_path = os.path.join(constants.ADQ_WORKING_FOLDER, str(project_id), combined_filename)

    # Create a PDF document
    with PdfPages(full_path) as pdf:
        # Save each chart as a separate page in the PDF
        for i, chart in enumerate(charts_list):
            # Save the chart as a PNG image
            image_path = f"{project_id}_chart_{i}.png"
            image_full_path = os.path.join(constants.ADQ_WORKING_FOLDER, str(project_id), image_path)
            chart.write_image(image_full_path, format='png')

            # Add the image to the PDF page
            fig = plt.figure(figsize=(8, 6))
            img = plt.imread(image_full_path)
            plt.imshow(img)
            plt.axis('off')
            pdf.savefig(fig)
            plt.close()

            # Remove the temporary image file
            os.remove(image_full_path)

    download_disabled = not os.path.exists(full_path)

    # Add download button
    with open(full_path, 'rb') as f:
        file_bytes = f.read()
        st.download_button(
            label='Download combined chart',
            data=file_bytes,
            file_name=combined_filename,
            mime='application/pdf',
            disabled=download_disabled
        )
