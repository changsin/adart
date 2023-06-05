import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

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
    df_tasks = None

    tasks_info = get_tasks_info()
    if len(tasks_info.tasks) > 0:
        df_tasks = pd.DataFrame([task.to_json() for task in tasks_info.tasks])
        df_tasks = df_tasks.rename(columns=lambda x: x.strip() if isinstance(x, str) else x)

        # Sort the DataFrame by project_id
        df_tasks = df_tasks.sort_values(by="project_id")
    else:
        st.write("No tasks to show")

    st.subheader("**Projects**")

    projects_info = get_projects_info()
    if projects_info.num_count > 0:
        # turn a class object to json dictionary to be processed by pandas dataframe
        df_projects = pd.DataFrame(projects_info.to_json()[constants.PROJECTS])
        df_projects = df_projects[constants.PROJECT_COLUMNS]
        # df_projects["% Done"] = np.where(df_projects["task_total_count"] == 0, 0,
        #                                  df_projects["task_done_count"] / df_projects["task_total_count"] * 100)

        grouped_tasks = df_tasks.groupby("project_id").sum().reset_index()
        df_projects = pd.merge(df_projects,
                               grouped_tasks[["project_id", "data_count", "object_count", "error_count"]],
                               left_on="id", right_on="project_id", how="left")
        # Calculate the task count for each project
        task_counts = df_tasks.groupby("project_id").size().reset_index(name="Task count")
        task_done_counts = df_tasks[df_tasks["state_name"] == "Done"].groupby("project_id").size().reset_index(name="Task done count")

        # Merge the task counts with the df_projects DataFrame
        df_projects = pd.merge(df_projects, task_counts, on="project_id", how="left")
        df_projects = pd.merge(df_projects, task_done_counts, on="project_id", how="left")
        # Fill missing values in task_done_counts with 0
        df_projects["Task done count"] = df_projects["Task done count"].fillna(0)

        # Calculate the percentage done for each project
        df_projects["% Done"] = (df_projects["Task done count"] / df_projects["Task count"]) * 100
        df_projects["% Done"] = df_projects["% Done"].fillna(0)  # Replace NaN with 0

        # Merge the task counts with the df_projects DataFrame
        df_projects = pd.merge(df_projects, task_counts, on="project_id", how="left")

        df_projects = df_projects.rename(
            columns={"data_count": "Image count", "object_count": "Label count",
                     "error_count": "Error count"})

        logger.info(f"projects: {df_projects}")
        df_projects["# of images"] = df_projects["data_total_count"]

        logger.info(df_projects)

        results_df = df_projects[
            ["id", "name", "Image count", "Label count", "Error count", "Task count_x", "Task done count", "% Done"]]
        results_df.columns = ["Id", "Name", "Image count", "Label count", "Error count", "Task count", "Task done count", "% Done"]

        # Use the custom table formatter for the "% Done" column
        results_df["% Done"] = results_df["% Done"].apply(bar_chart_formatter)
        # # Apply the bar chart formatter to the "% Done" column and return it as HTML
        # results_df["% Done"] = results_df["% Done"].apply(lambda x: bar_chart_formatter(x, width=150, height=10))

        # Assign the resulting DataFrame to a variable and render it as HTML
        results_df_html = results_df.to_html(escape=False, index=False)

        # Render the HTML table with the formatted "% Done" column
        st.write(results_df_html, unsafe_allow_html=True)
        # AgGrid(df_projects)

    if df_tasks is not None:
        st.subheader("**Tasks**")
        logger.info(df_tasks)
        # Render the DataFrame with status color as colored square using HTML and CSS
        st.write(
            df_tasks[["project_id", "id", "name", "data_count", "object_count", "error_count",
                      "annotator_fullname", "reviewer_fullname", "state_name"]]
            .rename(columns={
                "project_id": "Project id",
                "id": "Task id",
                "name": "Name",
                "data_count": "Image count",
                "object_count": "Label count",
                "error_count": "Error count",
                "annotator_fullname": "Annotated by",
                "reviewer_fullname": "Reviewed by",
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


def main():
    # Clear the sidebar
    st.sidebar.empty()
    # Clear the main page
    st.empty()

    st.markdown("# Dashboard")
    dashboard()
    #
    # menu = {
    #     "View Project": lambda: view_project(),
    # }
    #
    # # Create a sidebar with menu options
    # selected_action = st.sidebar.radio("Choose action", list(menu.keys()))
    # if selected_action:
    #     # Call the selected method based on the user's selection
    #     menu[selected_action]()


if __name__ == '__main__':
    if not is_authenticated():
        login()
    else:
        main()
        logout()
