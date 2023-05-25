from collections import namedtuple

import altair as alt
import pandas as pd
import shapely
import streamlit as st

import plotly.express as px

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

logger = get_logger(__name__)

Rectangle = namedtuple('Rectangle', 'xmin ymin xmax ymax')


def show_file_metrics():
    selected_project = select_project()
    if selected_project:

        data_files = get_data_files(selected_project.dir_name, is_thumbnails=True)
        #chart_aspect_ratios, chart_brightness = plot_aspect_ratios_brightness("### Aspect ratios",
                                                                              #data_files)
        #logger.info(selected_project)
        #data_files = get_data_files(selected_project.dir_name)
        #if data_files:
        chart_files_ctime, chart_file_sizes = plot_file_info("Data files info", data_files)
        col1, col2 = st.columns(2)
        if chart_files_ctime:
            display_chart(selected_project.id, "files_ctime", chart_files_ctime, column=col1)

        if chart_file_sizes:
            display_chart(selected_project.id, "file_sizes", chart_file_sizes, column=col2)

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
        chart_aspect_ratios, chart_brightness = plot_aspect_ratios_brightness("### Aspect ratios",
                                                                              data_files)
        col1, col2 = st.columns(2)
        if chart_aspect_ratios:
            display_chart(selected_project.id, "aspect_ratios", chart_aspect_ratios, column=col1)
        if chart_brightness:
            display_chart(selected_project.id, "brightness", chart_brightness, column=col2)

        show_download_charts_button(selected_project.id)
    else:
        st.write("No image data")


def get_label_metrics(label_files_dict: dict) -> (dict, dict, dict, dict):
    logger.info(f"label_files_dict {label_files_dict}")
    label_objects_dict = DataLabels.load_from_dict(label_files_dict)

    class_labels = dict()
    overlap_areas = dict()
    dimensions = dict()
    errors = dict()
    for label_file, data_labels in label_objects_dict.items():
        logger.info(f"get_label_metrics {label_file} {data_labels}")
        for image in data_labels.images:
            count = len(image.objects)
            for ob_id1 in range(count):
                object_cur = image.objects[ob_id1]
                label = object_cur.label
                if class_labels.get(label):
                    class_labels[label] += 1
                else:
                    class_labels[label] = 1

                if object_cur.verification_result:
                    error_code = object_cur.verification_result['error_code']
                    if errors.get(error_code):
                        errors[error_code] += 1
                    else:
                        errors[error_code] = 1

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
                        logger.warn("empty points in {}".format(image.objects[ob_id2].label))
                        continue

                    xtl2, ytl2, xbr2, ybr2 = DataLabels.Object.get_bounding_rectangle(image.objects[ob_id2])
                    rect2 = Rectangle(xtl2, ytl2, xbr2, ybr2)

                    overlap_area, max_area = calculate_overlapping_rect(rect1, rect2)

                    if overlap_area > 0:
                        overlap_percent = format(overlap_area/max_area, '.2f')
                        overlap_percent = float(overlap_percent) * 100
                        if overlap_areas.get(overlap_percent):
                            overlap_areas[overlap_percent] += 1
                        else:
                            overlap_areas[overlap_percent] = 1

    return class_labels, overlap_areas, dimensions, errors


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
        logger.info(label_files)
        if not label_files:
            st.warning("No label files")
            return

        class_labels, overlap_areas, dimensions, errors = get_label_metrics(label_files)

        chart_errors = plot_chart("Error Count", "error", "count", errors)
        if chart_errors:
            display_chart(selected_project.id, "error_count", chart_errors)

        chart_class_count = plot_chart("Class Count", "class", "count", class_labels)
        if chart_class_count:
            display_chart(selected_project.id, "class_count", chart_class_count)

        chart_overlap_areas = plot_chart("Overlap Areas",
                                         x_label="overlap %", y_label="count",
                                         data_dict=overlap_areas)
        if chart_overlap_areas:
            display_chart(selected_project.id, "overlap_areas", chart_overlap_areas)

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
            df_dimensions = pd.DataFrame([(k, *t) for k, v in dimensions.items() for t in v],
                                         columns=['filename', 'width', 'height', 'class'])

            chart_dimensions = px.scatter(df_dimensions, x='width', y='height', color='class',
                                        hover_data=['class', 'width', 'height', 'filename'],
                                        title="Label Dimensions")

            chart_dimensions.update_layout(width=600, height=400)

            if chart_dimensions:
                 display_chart(selected_project.id, "dimensions", chart_dimensions)

        show_download_charts_button(selected_project.id)


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
