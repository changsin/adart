import datetime as dt
import os

import altair as alt
import cv2
import pandas as pd
import streamlit as st
import utils
import constants


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

    # print(aspect_ratios)
    # print(brightness_values)
    # # Create a Pandas DataFrame from the aspect ratios
    # df_aspect_ratios = pd.DataFrame({
    #     'aspect_ratio': aspect_ratios.keys(),
    #     'count()': aspect_ratios.values()
    # })
    #
    # # Create a histogram of the aspect ratios using Altair
    # chart_aspect_ratios = alt.Chart(df_aspect_ratios).mark_bar().encode(
    #     x=alt.X('aspect_ratio'),
    #     y=alt.Y('count():Q', title='Count'),
    #     tooltip=['aspect_ratio', 'count()']
    # ).properties(
    #     title='Aspect Ratios of Images'
    # )
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

    # Create a histogram of the aspect ratios using Altair
    chart_aspect_ratios = alt.Chart(df_aspect_ratios).mark_bar().encode(
        x=alt.X('aspect_ratio'),
        y=alt.Y('count:Q', title='Count'),
        tooltip=['aspect_ratio', 'count:Q']
    ).properties(
        title='Aspect Ratios of Images'
    )
    chart_aspect_ratios = chart_aspect_ratios.interactive()  # make the chart interactive
    chart_aspect_ratios = chart_aspect_ratios.properties(
        width=600,
        height=400
    ).add_selection(
        alt.selection_interval(bind='scales', encodings=['x', 'y'])
    ).add_selection(
        alt.selection(type='interval', bind='scales', encodings=['x', 'y'])
    )

    brightness_values_list = [(k, v) for k, v in brightness_values.items()]
    # Create a Pandas DataFrame from the brightness
    df_brightness = pd.DataFrame(brightness_values_list, columns=['brightness', 'count'])

    # Create a histogram of the brightness using Altair
    chart_brightness = alt.Chart(df_brightness).mark_bar().encode(
        x=alt.X('brightness', bin=alt.Bin(step=10)),
        y=alt.Y('count:Q', title='Count'),
        tooltip=['brightness', 'count:Q']
    ).properties(
        title='Brightness of Images'
    )
    chart_brightness = chart_brightness.interactive()  # make the chart interactive
    chart_brightness = chart_brightness.properties(
        width=600,
        height=400
    ).add_selection(
        alt.selection_interval(bind='scales', encodings=['x', 'y'])
    ).add_selection(
        alt.selection(type='interval', bind='scales', encodings=['x', 'y'])
    )

    return chart_aspect_ratios, chart_brightness


@st.cache_data
def plot_file_sizes(title: str, files_dict: dict):
    if files_dict is None or len(files_dict.items()) == 0:
        return

    file_sizes = dict()
    for folder, files in files_dict.items():
        for file in files:
            file_stat = os.stat(os.path.join(folder, file))
            if file_sizes.get(file_stat.st_size):
                file_sizes[file_stat.st_size] = file_sizes[file_stat.st_size] + 1
            else:
                file_sizes[file_stat.st_size] = 1
    # return plot_chart(title, x_label='size', y_label='count', data_dict=file_sizes, chart_type="line")
    data = pd.DataFrame({
        'size': file_sizes.keys(),
        'count': file_sizes.values()
    })

    data['size'] = data['size'].astype(int)

    # # # Draw a line graph
    # # chart = alt.Chart(data).mark_line().encode(
    # #     x=alt.X('size', bin=True, title='File Size (bytes)'),
    # #     y='count()',
    # #     tooltip=['size', 'count()']
    # # ).properties(
    # #     title='File Size Distribution'
    # # )

    # Create a histogram using Altair
    chart = alt.Chart(data).mark_bar().encode(
        alt.X('size', bin=alt.Bin(maxbins=50), title='File Size (bytes)'),
        y='count()'
    ).properties(
        title='File Size Distribution'
    )

    # # Create a KDE plot using Altair
    # chart = alt.Chart(data).transform_density(
    #     'size',
    #     as_=['size', 'count'],
    # ).mark_area(opacity=0.5).encode(
    #     alt.X('size:Q', title='File Size (bytes)'),
    #     alt.Y('count:Q', title='Count')
    # )

    chart = chart.interactive()  # make the chart interactive
    chart = chart.properties(
        width=600,
        height=400
    ).add_selection(
        alt.selection_interval(bind='scales', encodings=['x', 'y'])
    ).add_selection(
        alt.selection(type='interval', bind='scales', encodings=['x', 'y'])
    )

    return chart


@st.cache_data
def plot_datetime(title: str, files_dict: dict):
    if files_dict is None or len(files_dict.items()) == 0:
        return

    ctime_dict = dict()
    for folder, files in files_dict.items():
        level = folder.count(os.sep)
        indent = '-' * level
        # st.markdown('{}📁({}) {}/'.format(indent, len(files), folder))
        with st.expander('📁({}) {}/'.format(len(files), folder)):
            for file in files:
                file_stat = os.stat(os.path.join(folder, file))
                dt_cdatetime = dt.datetime.fromtimestamp(file_stat.st_ctime)
                st.markdown("📄{} ({}) {}".format(file,
                                                 utils.humanize_bytes(file_stat.st_size),
                                                 dt_cdatetime.date()))
                ctime_object = dt_cdatetime.time()
                # Append date and time to x and y data lists
                ctime_dict[file] = (dt_cdatetime.date(), float(ctime_object.strftime('%H.%M')), file)

    df_ctime = pd.DataFrame.from_dict(ctime_dict, orient='index', columns=['date', 'time', 'file'])

    # convert the date column to a string representation
    df_ctime['date'] = df_ctime['date'].astype(str)

    chart_ctime = alt.Chart(df_ctime).mark_circle().encode(
        x='date',
        y='time',
        tooltip=['date', 'time', 'file']
        ).properties(
            title="Created Time"
        )

    # make the chart interactive
    chart_ctime = chart_ctime.interactive()
    chart_ctime = chart_ctime.properties(
        width=600,
        height=400
    ).add_selection(
        alt.selection_interval(bind='scales', encodings=['x', 'y'])
    ).add_selection(
        alt.selection(type='interval', bind='scales', encodings=['x', 'y'])
    )

    return chart_ctime


@st.cache_data
def plot_chart(title: str, x_label: str, y_label: str, data_dict: dict, chart_type="bar"):
    if data_dict is None or len(data_dict.items()) == 0:
        return

    data = pd.DataFrame({
        x_label: data_dict.keys(),
        y_label: data_dict.values()
    })

    # Create a histogram using Altair
    if chart_type == "circle":
        # Convert the date field to a datetime format
        # data[x_label] = pd.to_datetime(data[x_label])
        chart = alt.Chart(data).mark_circle(size=200).encode(
            x=alt.X(x_label),
            y=alt.Y(y_label),
            tooltip=[x_label, y_label]
        ).properties(
            title=title
        )
    elif chart_type == "line":
        chart = alt.Chart(data).mark_line().encode(
            x=alt.X(x_label),
            y=alt.Y(y_label),
            tooltip=[x_label, y_label]
        ).properties(
            title=title
        )
    else:
        chart = alt.Chart(data).mark_bar().encode(
            x=alt.X(x_label),
            y=alt.Y(y_label),
            tooltip=[x_label, y_label]
        ).properties(
            title=title
        )

    # make the chart interactive
    chart = chart.interactive()
    chart = chart.properties(
        width=600,
        height=400
    ).add_selection(
        alt.selection_interval(bind='scales', encodings=['x', 'y'])
    ).add_selection(
        alt.selection(type='interval', bind='scales', encodings=['x', 'y'])
    )

    return chart


def display_chart(project_id, name, chart):
    st.altair_chart(chart, use_container_width=True)

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
    charts = st.session_state[constants.CHARTS]
    if not charts.get(project_id):
        st.text("Nothing here")
        return

    combined_chart = alt.concat(*charts[project_id].values(), columns=len(charts[project_id]))
    # Create a temporary file
    combined_filename = "{}.{}.{}".format(project_id, "combined_charts", "html")
    full_path = os.path.join(constants.ADQ_WORKING_FOLDER, str(project_id), combined_filename)
    print(combined_chart)
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
