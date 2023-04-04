import datetime as dt
import os

import streamlit as st

import utils
# from streamlit_drawable_canvas import st_canvas
# from bokeh.plotting import figure
# from bokeh.models import ColumnDataSource, HoverTool
# from streamlit_bokeh_events import streamlit_bokeh_events

# import streamlit.components.v1 as components


def show_images(files_dict: dict):
    # Define the number of columns
    num_columns = 5

    for folder, files in files_dict.items():
        # # Calculate the number of rows needed based on the number of images and columns
        # num_rows = int(len(files) / num_columns) + (1 if len(files) % num_columns > 0 else 0)

        # Create a layout with the specified number of columns
        columns = st.columns(num_columns)
        for i, file in enumerate(files):
            with columns[i % num_columns]:
                full_path = os.path.join(folder, file)
                file_stat = os.stat(full_path)
                dt_datetime = dt.datetime.fromtimestamp(file_stat.st_ctime)
                print(full_path)
                st.image(full_path,
                         # use_column_width=True,
                         caption="{} {} {}".format(file,
                                                   utils.humanize_bytes(file_stat.st_size),
                                                   dt_datetime.date()),
                         width=100)
    #
    # # Define the JavaScript code to add a double-click event handler to all images
    # js_code = """
    # var images = document.getElementsByTagName("img");
    # for (var i = 0; i < images.length; i++) {
    #   images[i].addEventListener("dblclick", function() {
    #     var image_path = this.getAttribute("src");
    #     Streamlit.setComponentValue(image_path);
    #   });
    # }
    # """
    #
    # # Add the JavaScript code to the app
    # components.html('<script>{}</script>'.format(js_code))
    #
    # # Define a placeholder for the bigger image
    # bigger_image_placeholder = st.empty()
    #
    # # Wait for a double-click event on an image
    # image_path = st.session_state.get("image_path")
    # if image_path:
    #     display_bigger_image(image_path)
    #     bigger_image_placeholder.empty()
    # else:
    #     st.session_state["image_path"] = None
    #             # # Add a double-click event listener to the image using JavaScript
    #             # js_code = f"""
    #             # <script>
    #             # document.querySelectorAll(".streamlit-image-placeholder img")[{i}].addEventListener("dblclick", function() {{
    #             #     // Call the display_bigger_image function to display the bigger image
    #             #     var img_src = "{full_path}";
    #             #     var img_elem = document.createElement("img");
    #             #     img_elem.src = img_src;
    #             #     img_elem.onload = function() {{
    #             #         Streamlit.setFrameHeight();
    #             #     }};
    #             #     {st._get_report_ctx().enqueue("display_bigger_image", image=img_elem)}
    #             # }});
    #             # </script>
    #             # """
    #             # st.write(js_code, unsafe_allow_html=True)
    #
    #             # # Create a Bokeh figure and add the image to it
    #             # fig = figure(width=100, height=100, tools='pan,wheel_zoom')
    #             # source = ColumnDataSource({'image': [full_path]})
    #             # fig.image(image='image', x=0, y=0, dw=1, dh=1, source=source)
    #             #
    #             # # Add a hover tool to display the image name
    #             # hover = HoverTool(tooltips=[('Name', file)])
    #             # fig.add_tools(hover)
    #             #
    #             # # Add an event handler to zoom in on the image when clicked
    #             # result = streamlit_bokeh_events(fig, 'image_click', key=file, refresh_on_update=False, debounce_time=0)
    #             # if result:
    #             #     if 'image_click' in result:
    #             #         x_range = fig.x_range
    #             #         y_range = fig.y_range
    #             #         x, y = result['image_click']['x'], result['image_click']['y']
    #             #         x_range.start, x_range.end = x - 0.5, x + 0.5
    #             #         y_range.start, y_range.end = y - 0.5, y + 0.5
    #             #
    #             # # Display the image and caption
    #             # st.bokeh_chart(fig, use_container_width=True)
    #             # st.write("{} {} {}".format(file, utils.humanize_bytes(file_stat.st_size), dt_datetime.date()))


# Define the function that displays a bigger image
def display_bigger_image(image):
    st.image(image, width=None, caption=None)

# def annotate_image(image):
#     # Add annotation controls
#     with st_canvas(st.image(image, use_column_width=True).image_data, drawing_mode="freedraw", key="canvas"):
#         st.write("Draw on the image")

# # Add an event listener to the image using JavaScript
# js_code = """
# <script>
# document.querySelector("img").addEventListener("dblclick", function() {
#   // Create a Bokeh widget or plot
#   var plot = Bokeh.Plotting.figure();
#   // Add interactive controls or visualization to the plot
#   ...
#   // Add the plot to the Streamlit app
#   const plot_div = document.createElement("div");
#   plot_div.id = "plot";
#   document.body.appendChild(plot_div);
#   Bokeh.embed.embed_item(plot, "plot");
# });
# </script>
# """
# st.write(js_code, unsafe_allow_html=True)
