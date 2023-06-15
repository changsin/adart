from collections import namedtuple

import altair as alt
import pandas as pd
import shapely
import streamlit as st

import plotly.express as px
import io
from PIL import Image
import plotly.graph_objects as go
import os.path
import numpy as np
import base64
import dash
from dash import Dash
from dash import dcc
from dash import html
from src.common import constants, utils
from collections import OrderedDict


import io
from PIL import Image
import plotly.graph_objects as go
import os.path
import numpy as np
import base64
import dash
from dash import Dash
from dash import dcc
from dash import html
from src.common import constants, utils
from collections import OrderedDict



from src.common.charts import (
    display_chart,
    plot_aspect_ratios_brightness,
    plot_chart,
    plot_file_info,
    show_download_charts_button
)
from src.common.logger import get_logger
from src.models.data_labels import DataLabels
from .home import (
    is_authenticated,
    get_data_files,
    get_label_files,
    login,
    logout,
    select_project)
from src.pages.reviews import load_thumbnail

logger = get_logger(__name__)

Rectangle = namedtuple('Rectangle', 'xmin ymin xmax ymax')


def show_file_metrics():
    selected_project = select_project()
    if selected_project:

        data_files = get_data_files(selected_project.dir_name, is_thumbnails=True)
        #chart_aspect_ratios, chart_brightness = plot_aspect_ratios_brightness("### Aspect ratios",
                                                                              #data_files)
        chart_files_ctime, chart_file_sizes, table_files_ctime = plot_file_info("Data files info", data_files)

        col1, col2 = st.columns(2)
        if chart_files_ctime:
            display_chart(selected_project.id, "files_ctime", chart_files_ctime, table_files_ctime, column=col1)

        if chart_file_sizes:
            display_chart(selected_project.id, "file_sizes", chart_file_sizes, table_files_ctime, column=col2)

        # label_files = get_label_files(selected_project)
        # if label_files:
        #     chart_labels_ctime, chart_label_file_sizes = plot_file_info("Label files info",
        #                                                                 label_files)
        #     col1, col2 = st.columns(2)
        #     with col1:
        #         if chart_labels_ctime:
        #             display_chart(selected_project.id, "label_files_ctime", chart_labels_ctime, column=col1)
        #
        #     with col2:
        #         if chart_label_file_sizes:
        #             display_chart(selected_project.id, "label_file_sizes", chart_label_file_sizes, column=col2)

        show_download_charts_button(selected_project.id)


def show_image_metrics():
    selected_project = select_project()
    if selected_project:
        data_files = get_data_files(selected_project.dir_name, is_thumbnails=True)
        chart_aspect_ratios, chart_brightness, table_aspect_ratios, table_brightness  = plot_aspect_ratios_brightness("### Aspect ratios",
                                                                              data_files)
        col1, col2 = st.columns(2)
        if chart_aspect_ratios:
            display_chart(selected_project.id, "aspect_ratios", chart_aspect_ratios, table_aspect_ratios, column=col1)
        if chart_brightness:
            display_chart(selected_project.id, "brightness", chart_brightness, table_brightness, column=col2)

        show_download_charts_button(selected_project.id)
    else:
        st.write("No image data")


def get_label_metrics(label_files_dict: dict) -> (dict, dict, dict, dict):
    label_objects_dict = DataLabels.load_from_dict(label_files_dict)

    class_labels = dict()
    overlap_areas = dict()
    dimensions = dict()
    errors = dict()
    error_columns = set()
    class_columns = set()

    image_table_data = {
        'filename': [],
        'total_classes': [],
        'class_names': []
    }

    for label_file, data_labels in label_objects_dict.items():

        for image in data_labels.images:
            count = len(image.objects)
            class_names = set()
            error_counts = dict()
            class_counts = dict()  # Track class counts per image

            for ob_id1 in range(count):
                object_cur = image.objects[ob_id1]
                label = object_cur.label
                class_names.add(label)
                class_counts[label] = class_counts.get(label, 0) + 1
                if class_labels.get(label):
                    class_labels[label] += 1
                else:
                    class_labels[label] = 1
                class_columns.add(label)

                if object_cur.verification_result:
                    error_code = object_cur.verification_result['error_code']
                    if errors.get(error_code):
                        errors[error_code] += 1
                    else:
                        errors[error_code] = 1

                    if error_counts.get(error_code):
                        error_counts[error_code] += 1
                    else:
                        error_counts[error_code] = 1

                    error_columns.add(error_code)
                #else:
                    #errors = dict()
                    #error_counts = dict()
                    #error_columns = set()
                
        
                if not object_cur.points:
                    logger.warn("empty points in {}".format(object_cur.label))
                    continue

                xtl1, ytl1, xbr1, ybr1 = DataLabels.Object.get_bounding_rectangle(object_cur)
                rect1 = Rectangle(xtl1, ytl1, xbr1, ybr1)
                width1 = rect1.xmax - rect1.xmin
                height1 = rect1.ymax - rect1.ymin

                if dimensions.get(image.name):
                    dimensions[image.name].append((width1, height1, image.objects[ob_id1].label))
                else:
                    dimensions[image.name] = [(width1, height1, image.objects[ob_id1].label)]

                for ob_id2 in range(ob_id1 + 1, count):
                    if not image.objects[ob_id2].points:
                        continue

                    xtl2, ytl2, xbr2, ybr2 = DataLabels.Object.get_bounding_rectangle(image.objects[ob_id2])
                    rect2 = Rectangle(xtl2, ytl2, xbr2, ybr2)

                    overlap_area, max_area = calculate_overlapping_rect(rect1, rect2)

                    if overlap_area > 0:
                        overlap_percent = format(overlap_area / max_area, '.2f')
                        overlap_percent = float(overlap_percent) * 100
                        if overlap_areas.get(overlap_percent):
                            overlap_areas[overlap_percent] += 1
                        else:
                            overlap_areas[overlap_percent] = 1

            image_table_data['filename'].append(image.name)
            image_table_data['total_classes'].append(len(class_names))
            image_table_data['class_names'].append(", ".join(class_names))

            # Add class columns dynamically
            for label in class_columns:
                if label not in image_table_data:
                    image_table_data[label] = [class_counts.get(label, 0)]
                else:
                    image_table_data[label].append(class_counts.get(label, 0))
            # Add error columns dynamically
            for error_code in error_columns:
                if error_code not in image_table_data:
                    image_table_data[error_code] = [error_counts.get(error_code, 0)]
                else:
                    image_table_data[error_code].append(error_counts.get(error_code, 0))

            
    required_keys = ['Mis-tagged', 'Untagged', 'Over-tagged', 'Range_error', 'Attributes_error']

    for key in required_keys:
        if key not in errors:
            errors[key] = ['0']
    # Make sure all arrays have the same length
    max_length = max(len(value) for value in image_table_data.values())

    for key, value in image_table_data.items():
        if len(value) < max_length:
            image_table_data[key].extend([0] * (max_length - len(value)))
    # Add missing error columns with 0 count
    error_names = ['Mis-tagged', 'Untagged', 'Over-tagged', 'Range_error', 'Attributes_error']

    for error_code in error_names:
        if error_code not in image_table_data:
            image_table_data[error_code] = [0] * len(image_table_data['filename'])

    image_table = pd.DataFrame(image_table_data)
    # Check if all values in each row are 0 and delete the row
    image_table = image_table.loc[~(image_table == 0).all(axis=1)]
    return class_labels, overlap_areas, dimensions, errors, image_table





    #return class_labels, overlap_areas, dimensions, errors, image_table


def triangle_area(vertices):
    # Calculates the area of a triangle given its vertices using the cross product formula
    x1, y1 = vertices[0]
    x2, y2 = vertices[1]
    x3, y3 = vertices[2]
    return abs((x2-x1)*(y3-y1) - (x3-x1)*(y2-y1)) / 2


def polygon_area(vertices):
    # Calculates the area of a polygon given its vertices using the shoelace formula
    x = [vertex[0] for vertex in vertices]
    y = [vertex[1] for vertex in vertices]
    return 0.5 * abs(sum(x[i]*y[i+1] - x[i+1]*y[i] for i in range(-1,len(x)-1)))


def overlapping_area(poly1, poly2):
    # Calculates the overlapping area of two polygons
    intersect = poly1.intersection(poly2)
    if intersect.is_empty:
        return 0
    triangles = []
    for poly in [poly1, poly2]:
        points = list(poly.exterior.coords)
        for i in range(poly.interiors.__len__()):
            points += list(poly.interiors[i].coords)
        for j in range(-1, len(points)-2):
            triangles.append((points[0], points[j+1], points[j+2]))
    contained_triangles = []
    for triangle in triangles:
        in_poly1 = poly1.contains(shapely.geometry.Point(triangle[0])) and poly1.contains(shapely.geometry.Point(triangle[1])) and poly1.contains(shapely.geometry.Point(triangle[2]))
        in_poly2 = poly2.contains(shapely.geometry.Point(triangle[0])) and poly2.contains(shapely.geometry.Point(triangle[1])) and poly2.contains(shapely.geometry.Point(triangle[2]))
        if in_poly1 and not in_poly2:
            contained_triangles.append(triangle)
        elif in_poly2 and not in_poly1:
            contained_triangles.append(triangle)
    overlapping_area = sum(triangle_area(triangle) for triangle in triangles) - sum(triangle_area(triangle) for triangle in contained_triangles)
    return overlapping_area


def calculate_overlapping_rect(a, b):
    overlapping_area = 0.0
    max_area = 0.0

    dx = min(a.xmax, b.xmax) - max(a.xmin, b.xmin)
    dy = min(a.ymax, b.ymax) - max(a.ymin, b.ymin)
    if (dx >= 0) and (dy >= 0):
        area1 = (a.xmax - a.xmin) * (a.ymax - a.ymin)
        area2 = (b.xmax - b.xmin) * (b.ymax - b.ymin)

        max_area = max(area1, area2)
        overlapping_area = dx*dy

    return overlapping_area, max_area


def show_label_metrics():
    selected_project = select_project()
    if selected_project:
        label_files = get_label_files(selected_project)
        if not label_files:
            st.warning("No label files")
            return

        class_labels, overlap_areas, dimensions, errors, image_table = get_label_metrics(label_files)
        
        if errors:
            chart_errors, table_errors = plot_chart("Error Count", "error", "count", errors)
            display_chart(selected_project.id, "error_count", chart_errors, table_errors)
            show_table = st.button("Show Table", key="show_table1")
            if show_table:
                st.table(table_errors)
                collapse_table = st.button("Collapse Table", key="collapse_table1")
                if collapse_table:
                    st.table_errors([])  # Empty table to collapse the view
        else:
            st.write("No errors were created.")
        chart_class_count, table_class = plot_chart("Class Count", "class", "count", class_labels)
        if chart_class_count:
            display_chart(selected_project.id, "class_count", chart_class_count, table_class)
            show_table = st.button("Show Table", key="show_table2")
            if show_table:
                st.table(table_class)
                collapse_table = st.button("Collapse Table", key="collapse_table2")
                if collapse_table:
                    st.table_class([])  # Empty table to collapse the view

        chart_overlap_areas, table_overlap_areas = plot_chart("Overlap Areas",
                                         x_label="overlap %", y_label="count",
                                         data_dict=overlap_areas)
        if chart_overlap_areas:
            display_chart(selected_project.id, "overlap_areas", chart_overlap_areas, table_overlap_areas)
            show_table = st.button("Show Table", key="show_table3")
            if show_table:
                st.table(table_overlap_areas)
                collapse_table = st.button("Collapse Table", key="collapse_table3")
                if collapse_table:
                    st.table_overlap_areas([])  # Empty table to collapse the view

        # if dimensions:
        #     df_dimensions = pd.DataFrame([(k, *t) for k, v in dimensions.items() for t in v],
        #                                  columns=['filename', 'width', 'height', 'class'])
        #     chart_dimensions = alt.Chart(df_dimensions).mark_circle().encode(
        #         x='width',
        #         y='height',
        #         color='class',
        #         tooltip=['class', 'width', 'height', 'filename']
        #         ).properties(
        #             title="Label Dimensions"
        #         )
        #
        #     # make the chart interactive
        #     chart_dimensions = chart_dimensions.interactive()
        #     chart_dimensions = chart_dimensions.properties(
        #         width=600,
        #         height=400
        #     ).add_selection(
        #         alt.selection_interval(bind='scales', encodings=['x', 'y'])
        #     ).add_selection(
        #         alt.selection(type='interval', bind='scales', encodings=['x', 'y'])
        #     )
        #
        #     if chart_dimensions:
        #         display_chart(selected_project.id, "dimensions", chart_dimensions)

        #Using Plotly

        if dimensions:
            # df_dimensions = pd.DataFrame([(k, *t) for k, v in dimensions.items() for t in v],
            #                              columns=['filename', 'width', 'height', 'class'])
            #
            # chart_dimensions = px.scatter(df_dimensions, x='width', y='height', color='class',
            #                             hover_data=['class', 'width', 'height', 'filename'],
            #                             title="Label Dimensions")
            #
            # chart_dimensions.update_layout(width=600, height=400)

            df_dimensions = pd.DataFrame([(k, *t) for k, v in dimensions.items() for t in v],
                                         columns=['filename', 'width', 'height', 'class'])

            table_dimensions = df_dimensions

            # Generate thumbnails
            project_folder = selected_project.dir_name
            thumbnail_filenames = get_data_files(project_folder, is_thumbnails=True)

            thumbnails = []

            for file in thumbnail_filenames["."]:
                thumbnail_image = load_thumbnail(file)
                thumbnails.append(thumbnail_image)

            # Add thumbnails to the DataFrame
            df_dimensions['thumbnail'] = thumbnail_filenames

            # Create a list of image source paths
            image_sources = [thumbnail_filenames.get(file, '') for file in df_dimensions['filename']]

            # Filter out entries with missing image paths or empty values
            valid_indices = [i for i, source in enumerate(image_sources) if source]

            # Filter the data frame and image sources
            df_dimensions_filtered = df_dimensions.iloc[valid_indices]
            image_sources_filtered = [image_sources[i] for i in valid_indices]

            #Dash Version
            # Create a Dash app
            app = dash.Dash(__name__)

            # Define the custom hover template
            hover_template = (
                "<b>Class:</b> %{customdata[0]}<br>"
                "<b>Width:</b> %{customdata[1]}<br>"
                "<b>Height:</b> %{customdata[2]}<br>"
                '<img src="data:image/png;base64, %{customdata[3]}" alt="Thumbnail" width="100">'
            )

            # Encode the thumbnails as base64 strings
            encoded_thumbnails = []
            for filename in df_dimensions['filename']:
                thumbnail_path = thumbnail_filenames.get(filename, '')
                if thumbnail_path:
                    with open(thumbnail_path, 'rb') as f:
                        encoded_thumbnail = base64.b64encode(f.read()).decode('utf-8')
                        encoded_thumbnails.append(encoded_thumbnail)
                else:
                    encoded_thumbnails.append('')

            # Create a copy of the customdata array with an additional column for the encoded thumbnails
            customdata_with_thumbnails = df_dimensions[['class', 'width', 'height']].copy()
            customdata_with_thumbnails['thumbnail'] = encoded_thumbnails

            # Assign a numeric value to each unique class label
            class_labels = customdata_with_thumbnails['class'].unique()
            class_mapping = {label: i for i, label in enumerate(class_labels)}
            class_numeric = customdata_with_thumbnails['class'].map(class_mapping)

            # Create the scatter plot with custom hover template
            # chart_dimensions = go.Figure(
            #     data=go.Scatter(
            #         x=customdata_with_thumbnails['width'],
            #         y=customdata_with_thumbnails['height'],
            #         mode='markers',
            #         marker=dict(color='class'),
            #         hovertemplate=hover_template,
            #         customdata=customdata_with_thumbnails.values.T,
            #     ),
            #
            #     layout=go.Layout(
            #         title="Label Dimensions",
            #         width=600,
            #         height=400
            #     )
            #)

            #this gets you the chart in the normal format as a standin
            chart_dimensions = px.scatter(df_dimensions, x='width', y='height', color='class',
                                          hover_data=['class', 'width', 'height', 'filename'],
                                          title="Label Dimensions")
            chart_dimensions.update_layout(width=600, height=400)


            #chart_dimensions.update_traces(hoverinfo="none", hovertemplate=None)

            # Convert the chart to a Dash Graph component
            graph_dimensions = dcc.Graph(figure=chart_dimensions)

            # Create the app layout
            app.layout = html.Div(children=[
                graph_dimensions
            ])

            #dash_app_html = app.to_html()
            app.debug = True

            # Render the Dash app as an iframe in Streamlit
            #st.markdown(dash_app_html, unsafe_allow_html=True)
            #st.title('Dash Plot')

            #st.components.v1.html(app.index())

            #end Dash version


            #Plotly version
            # Define the custom hover template
            # hover_template = (
            #     "<b>Class:</b> %{customdata[0]}<br>"
            #     "<b>Width:</b> %{customdata[1]}<br>"
            #     "<b>Height:</b> %{customdata[2]}<br>"
            #     "<b>Height:</b> %{customdata[3]}<br>"
            #     #'<img src="data:image/png;base64, %{customdata[3]}" alt="Thumbnail" width="100">'
            # )
            #
            # # Encode the thumbnails as base64 strings
            # encoded_thumbnails = []
            # logger.info(f"*******thumbnail info {thumbnail_filenames}")
            #
            # for filename in thumbnail_filenames:
            #     with open(filename, 'rb') as f:
            #         encoded_thumbnail = base64.b64encode(f.read()).decode('utf-8')
            #         encoded_thumbnails.append(encoded_thumbnail)
            #
            # logger.info(f"*******thumbnail info{thumbnail_path} {thumbnail_filenames}")
            #
            # # Assign a numeric value to each unique class label
            # class_labels = df_dimensions['class'].unique()
            # class_mapping = {label: i for i, label in enumerate(class_labels)}
            # class_numeric = df_dimensions['class'].map(class_mapping)
            #
            # # Create the scatter plot with custom hover template
            # chart_dimensions = go.Figure(
            #     data=go.Scatter(
            #         x=df_dimensions['width'],
            #         y=df_dimensions['height'],
            #         mode='markers',
            #         marker=dict(color=class_numeric),
            #         hoverinfo="none",  # Disable default hover labels
            #         customdata=encoded_thumbnails,  # Use encoded thumbnails as custom data
            #     ),
            #     layout=go.Layout(
            #         title="Label Dimensions",
            #         width=600,
            #         height=400
            #     )
            # )
            #
            #
            #
            # # Update the customdata with encoded thumbnails
            # #for i, encoded_thumbnail in enumerate(encoded_thumbnails):
            # #    chart_dimensions.data[0].customdata[i] += (encoded_thumbnail,)
            #
            # # Add the image_sources_array as a trace-level customdata
            # #chart_dimensions.data[0].update(
            # #    customdata=np.column_stack((chart_dimensions.data[0].customdata, image_sources_array)))

            #app.run_server(debug=True)
            if chart_dimensions:
                display_chart(selected_project.id, "dimensions", chart_dimensions, table_dimensions)
            

        image_table = image_table[ list(image_table.columns)]
        show_download_charts_button(selected_project.id)
        dir_name = selected_project.name

        # Create download dropdown button for Excel or CSV file
        download_label = "Download the Combined Error Data Statistics"
        download_options = ["CSV", "Excel"]
        download_format = st.selectbox(download_label, download_options)
        if " " in dir_name:
            dir_name = dir_name.replace(" ", "_")
        project_folder = os.path.join(os.getcwd(),str(dir_name))
        # Check if the project folder exists
        if not os.path.exists(project_folder):
            # Create the project folder if it doesn't exist
            os.makedirs(project_folder)

        if download_format == "CSV":
            csv_filename = f"{selected_project.name}_data.csv"
            csv_full_path = os.path.join(project_folder, csv_filename)

            if os.path.exists(csv_full_path):
                os.remove(csv_full_path)  # Remove the existing file

            with open(csv_full_path, "w", newline="") as f:
                image_table.to_csv(f, index=False)

            with open(csv_full_path, "rb") as f:
                file_bytes = f.read()
                st.download_button(
                    label="Download CSV",
                    data=file_bytes,
                    file_name=csv_filename,
                    mime="text/csv"
                )
        elif download_format == "Excel":
            excel_filename = f"{selected_project.name}_data.xlsx"
            excel_full_path = os.path.join(project_folder, excel_filename)
            #excel_full_path = os.path.join(os.getcwd(), excel_filename)

            # Create a new Excel writer object
            with pd.ExcelWriter(excel_full_path, engine="openpyxl") as writer:
                image_table.to_excel(writer, index=False, header=True)

            with open(excel_full_path, "rb") as f:
                file_bytes = f.read()
                st.download_button(
                    label="Download Excel",
                    data=file_bytes,
                    file_name=excel_filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
def main():
    # Clear the sidebar
    st.sidebar.empty()
    # Clear the main page
    st.empty()

    menu = {
        "Show file metrics": lambda: show_file_metrics(),
        "Show image metrics": lambda: show_image_metrics(),
        "Show label metrics": lambda: show_label_metrics(),
    }

    # Create a sidebar with menu options
    selected_action = st.sidebar.radio("Choose action", list(menu.keys()))

    if selected_action:
        # Call the selected method based on the user's selection
        menu[selected_action]()


if __name__ == '__main__':
    if not is_authenticated():
        login()
    else:
        main()
        logout()
