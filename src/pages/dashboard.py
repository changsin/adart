import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from st_aggrid import AgGrid

from src.common import constants
from src.common.logger import get_logger
from .home import (
    api_target,
    get_projects_info,
    get_tasks_info,
    is_authenticated,
    login,
    logout,
    select_project)

logger = get_logger(__name__)


def view_project():
    selected_project = select_project(is_sidebar=True)

    if selected_project:
        st.markdown("# Project")
        st.dataframe(pd.DataFrame(selected_project.to_json(), index=[0]))

        extended_props = selected_project.extended_properties
        if extended_props:
            st.markdown("## Model validation information")
            st.dataframe(pd.DataFrame.from_dict(extended_props,
                                                orient='index'))

        st.markdown("# Tasks")
        tasks_info = get_tasks_info()
        tasks = tasks_info.get_tasks_by_project_id(selected_project.id)
        tasks_json = [task.to_json() for task in tasks]
        st.dataframe(pd.DataFrame(tasks_json))

    st.markdown("### Annotation error types")
    annotation_errors_dict = api_target().list_annotation_errors()
    st.dataframe(annotation_errors_dict)

    st.markdown("### State types")
    states_dict = api_target().list_states()
    st.dataframe(states_dict)

    st.markdown("### Annotation types")
    states_dict = api_target().list_annotation_types()
    st.dataframe(states_dict)

# def model_validation_dashboard():
#     projects_info = get_projects_info()
#     model_projects = []
#     for project in projects_info.projects:
#         if project.extended_properties:
#             model_projects.append(project)
#
#     for model_project in model_projects:
#         model_tasks = get_tasks(model_project.id)
#
#         for model_task in model_tasks:
#             model_task.

# Define a custom table formatter to display the horizontal bar graph in the table


def bar_chart_formatter(val):
    # Create a horizontal bar graph showing the percentage done for the current project
    fig, ax = plt.subplots(figsize=(2, 0.5))
    ax.barh(0, val, color="#1f77b4")
    ax.barh(0, 100 - val, left=val, color="#d3d3d3")
    ax.set_xlim(0, 100)
    ax.set_xticks([])
    ax.set_yticks([])
    plt.close()

    # Return the HTML code to display the bar graph in the table
    return f"<div style='display:flex;align-items:center;'><div>{val:.1f}%</div><div style='margin-left:10px;width:100px;height:10px;background-color:#d3d3d3;border-radius:5px;'><div style='width:{val}%;height:100%;background-color:#1f77b4;border-radius:5px;'></div></div></div>"


def dashboard():
    st.subheader("**Projects**")
    # df_projects = pd.DataFrame(columns=constants.PROJECT_COLUMNS)

    projects_info = get_projects_info()
    if projects_info.num_count > 0:
        # turn a class object to json dictionary to be processed by pandas dataframe
        df_projects = pd.DataFrame(projects_info.to_json()[constants.PROJECTS])
        df_projects = df_projects[constants.PROJECT_COLUMNS]
        # logger.info(df_projects.apply())
        # Calculate percentage of tasks done using a vectorized operation
        df_projects["% Done"] = df_projects["task_done_count"] / df_projects["task_total_count"] * 100 \
            if df_projects["task_total_count"].any() != 0 else 0
        df_projects["# of images"] = df_projects["total_count"]

        # Select only the relevant columns and display the results in a table
        results_df = df_projects[["id", "name", "# of images", "% Done"]]
        results_df.columns = ["id", "Name", "# of images", "% Done"]
        # st.table(results_df)

        # Use the custom table formatter for the "% Done" column
        results_df["% Done"] = results_df["% Done"].apply(bar_chart_formatter)
        # # Apply the bar chart formatter to the "% Done" column and return it as HTML
        # results_df["% Done"] = results_df["% Done"].apply(lambda x: bar_chart_formatter(x, width=150, height=10))

        # Assign the resulting DataFrame to a variable and render it as HTML
        results_df_html = results_df.to_html(escape=False, index=False)

        # Render the HTML table with the formatted "% Done" column
        st.write(results_df_html, unsafe_allow_html=True)
        # AgGrid(df_projects)

    st.subheader("**Tasks**")
    tasks_info = get_tasks_info()
    if len(tasks_info.tasks) > 0:
        df_tasks = pd.DataFrame([task.to_json() for task in tasks_info.tasks])
        df_tasks = df_tasks.rename(columns=lambda x: x.strip() if isinstance(x, str) else x)

        logger.info(df_tasks)
        # Render the DataFrame with status color as colored square using HTML and CSS
        st.write(
            df_tasks[["project_id", "id", "reviewer_fullname", "state_name"]]
            .rename(columns={
                "project_id": "Project id",
                "id": "Task id",
                "reviewer_fullname": "Assigned to",
                "state_name": "Status"
            })
            .to_html(
                escape=False,
                index=False,
                justify="center",
                classes="table-hover",
                col_space="2px",
                formatters={
                    "Status": lambda
                        x: f'<div style="background-color:{"red" if x == "New" else "orange" if x == "Working" else "green"}; color:white; border-radius:4px; padding:4px;">{x}<div style="background-color:{"red" if x == "New" else "yellow" if x == "Working" else "green"}; height:12px; width:12px; border-radius:50%; display:inline-block; margin-left:4px;"></div></div>',
                }
            ),
            unsafe_allow_html=True
        )
    else:
        st.write("No tasks to show")


def main():
    # Clear the sidebar
    st.sidebar.empty()
    # Clear the main page
    st.empty()

    st.markdown("# Dashboard")
    dashboard()

    menu = {
        "View Project": lambda: view_project(),
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
