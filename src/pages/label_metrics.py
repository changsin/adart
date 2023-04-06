from collections import namedtuple

import shapely

import importlib.util

spec = importlib.util.find_spec("src")
if spec is None:
    import sys
    from pathlib import Path

    path_root = Path(__file__).parents[2]
    sys.path.append(str(path_root))

from src.common.charts import *
from src.home import select_project
from src.models.adq_labels import AdqLabels
from src.models.dart_labels import DartLabels

Rectangle = namedtuple('Rectangle', 'xmin ymin xmax ymax')


def load_label_file(folder: str, label_file: str) -> DartLabels:
    """
    :param folder: parent folder
    :param label_file: label filename
    :return: DartLabels object
    """
    json_labels = utils.from_file("{}",
                                  folder,
                                  label_file)
    adq_labels = AdqLabels.from_json(json_labels)
    # convert to dart label format for easier processing
    return DartLabels.from_adq_labels(adq_labels)


def load_label_files(label_files_dict: dict) -> dict:
    """
    :param label_files_dict: label files with key=folder value=label filename
    :return: a dictionary with key=label filename value=DartLabels
    """
    label_objects_dict = {}

    if label_files_dict and len(label_files_dict.items()) > 0:
        for folder, label_files in label_files_dict.items():
            for label_file in label_files:
                label_objects_dict[label_file] = load_label_file(folder, label_file)

    return label_objects_dict


def get_label_metrics(label_files_dict: dict) -> (dict, dict, dict):
    label_objects_dict = load_label_files(label_files_dict)

    class_labels = dict()
    overlap_areas = dict()
    dimensions = dict()
    for label_file, dart_labels in label_objects_dict.items():
        for image in dart_labels.images:
            count = len(image.objects)
            for ob_id1 in range(count):
                label = image.objects[ob_id1].label
                if class_labels.get(label):
                    class_labels[label] += 1
                else:
                    class_labels[label] = 1

                xtl1, ytl1, xbr1, ybr1 = image.objects[ob_id1].points
                rect1 = Rectangle(xtl1, ytl1, xbr1, ybr1)
                width1 = rect1.xmax - rect1.xmin
                height1 = rect1.ymax - rect1.ymin
                dimensions[image.name] = (width1, height1, image.objects[ob_id1].label)

                for ob_id2 in range(ob_id1 + 1, count):
                    xtl2, ytl2, xbr2, ybr2 = image.objects[ob_id2].points
                    rect2 = Rectangle(xtl2, ytl2, xbr2, ybr2)

                    overlap_area, max_area = calculate_overlapping_rect(rect1, rect2)

                    if overlap_area > 0:
                        overlap_percent = format(overlap_area/max_area, '.2f')
                        overlap_percent = float(overlap_percent) * 100
                        if overlap_areas.get(overlap_percent):
                            overlap_areas[overlap_percent] += 1
                        else:
                            overlap_areas[overlap_percent] = 1

    return class_labels, overlap_areas, dimensions


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


def main():
    selected_project = select_project()
    if selected_project:
        if not selected_project.label_files:
            st.write("No labels!")
            return

        class_labels, overlap_areas, dimensions = get_label_metrics(selected_project.label_files)

        chart_class_count = plot_chart("Class Count", "class", "count", class_labels)
        if chart_class_count:
            display_chart(selected_project.id, "class_count", chart_class_count)

        chart_overlap_areas = plot_chart("Overlap Areas",
                                         x_label="overlap %", y_label="count",
                                         data_dict=overlap_areas)
        if chart_overlap_areas:
            display_chart(selected_project.id, "overlap_areas", chart_overlap_areas)

        # create DataFrame from dictionary
        df_dimensions = pd.DataFrame.from_dict(dimensions, orient='index', columns=['width', 'height', 'class'])
        chart_dimensions = alt.Chart(df_dimensions).mark_circle().encode(
            x='width',
            y='height',
            color='class',
            tooltip=['class', 'width', 'height']
            ).properties(
                title="Dimensions of Labels"
            )

        # make the chart interactive
        chart_dimensions = chart_dimensions.interactive()
        chart_dimensions = chart_dimensions.properties(
            width=600,
            height=400
        ).add_selection(
            alt.selection_interval(bind='scales', encodings=['x', 'y'])
        ).add_selection(
            alt.selection(type='interval', bind='scales', encodings=['x', 'y'])
        )

        if chart_dimensions:
            display_chart(selected_project.id, "dimensions", chart_dimensions)

        show_download_charts_button(selected_project.id)


if __name__ == '__main__':
    main()
