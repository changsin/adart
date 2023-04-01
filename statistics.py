import datetime as dt
import os

import altair as alt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
import cv2


def plot_aspect_ratios(title: str, files_dict: dict):
    st.markdown(title)

    if files_dict is None or len(files_dict.items()) == 0:
        return

    # Initialize a list to store the aspect ratios
    aspect_ratios = []
    brightness_values = []

    # Loop through all the files in the folder and calculate their aspect ratios
    for folder, files in files_dict.items():
        for file in files:
            image_path = os.path.join(folder, file)
            # Read the image using opencv-python
            img = cv2.imread(image_path)

            # Get the width and height of the image
            height, width, _ = img.shape

            # Calculate the aspect ratio
            aspect_ratio = width / height
            aspect_ratios.append(aspect_ratio)

            # Convert the image to grayscale
            gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # Calculate the average brightness of the image
            brightness = gray_img.mean()
            brightness_values.append(brightness)

    # Create a Pandas DataFrame from the aspect ratios
    df_aspect_ratios = pd.DataFrame({'aspect_ratio': aspect_ratios})

    # Create a histogram of the aspect ratios using Altair
    chart_aspect_ratios = alt.Chart(df_aspect_ratios).mark_bar().encode(
        x=alt.X('aspect_ratio', bin=True),
        y='count()',
        tooltip=['aspect_ratio', 'count()']
    ).properties(
        title='Aspect Ratios of Images'
    )

    # Display the histogram in Streamlit
    st.altair_chart(chart_aspect_ratios, use_container_width=True)

    df_brightness = pd.DataFrame({'brightness': brightness_values})

    # Create a histogram of the aspect ratios using Altair
    chart_brightness = alt.Chart(df_brightness).mark_bar().encode(
        x=alt.X('brightness', bin=True),
        y='count()',
        tooltip=['brightness', 'count()']
    ).properties(
        title='Brightness of Images'
    )

    # Plot the brightness values using Matplotlib
    st.altair_chart(chart_brightness, use_container_width=True)


def plot_file_sizes(title: str, files_dict: dict):
    st.markdown(title)

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

    # # Create some example data
    data = pd.DataFrame({
        'x': file_sizes.keys(),
        'y': file_sizes.values()
    })

    # Draw the line graph
    chart = alt.Chart(data).mark_line().encode(
        x='x',
        y='y'
    )

    st.altair_chart(chart, use_container_width=True)


def plot_datetime(title: str, files_dict: dict):
    st.markdown(title)

    if files_dict is None or len(files_dict.items()) == 0:
        return

    x_data = []
    y_data = []
    for folder, files in files_dict.items():
        level = folder.count(os.sep)
        indent = '-' * level
        # st.markdown('{}📁({}) {}/'.format(indent, len(files), folder))
        with st.expander('{}📁({}) {}/'.format(indent, len(files), folder)):
            for file in files:
                file_stat = os.stat(os.path.join(folder, file))
                dt_datetime = dt.datetime.fromtimestamp(file_stat.st_ctime)
                st.markdown("📄{} ({}B)(@{})".format(file, file_stat.st_size, dt_datetime))
                date_object = dt_datetime.date()
                time_object = dt_datetime.time()

                # Append date and time to x and y data lists
                x_data.append(date_object)
                y_data.append(float(time_object.strftime('%H.%M')))

    # Define the range of dot sizes
    min_size = 10
    max_size = 100

    # Calculate the size of each dot based on the number of data points
    sizes = np.linspace(min_size, max_size, len(x_data)) * 10

    # Plot data as a scatter plot
    fig, ax = plt.subplots(figsize=(10, 5))
    # Add legend and title to the plot
    # ax.legend(['File Creation Time'])
    ax.set_title("File Creation Time")
    ax.scatter(x_data, y_data, s=sizes, marker='o')

    # Set X-axis label
    ax.set_xlabel('Date')
    plt.xticks(rotation=45)

    # Set Y-axis label
    ax.set_ylabel('Time of the Day')

    # Set X-axis range
    start_date = min(x_data)
    end_date = max(x_data)
    # start_date = datetime.date(2023, 2, 1)
    # end_date = datetime.date(2023, 3, 1)
    ax.set_xlim(start_date, end_date)

    # # Add labels to the dots
    # for i, (x, y) in enumerate(zip(x_data, y_data)):
    #     ax.text(x, y, "*", fontsize=20)
    # Display plot
    st.pyplot(fig)
