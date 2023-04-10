import importlib.util
import os.path

spec = importlib.util.find_spec("src")
if spec is None:
    import sys
    from pathlib import Path

    path_root = Path(__file__).parents[1]
    sys.path.append(str(path_root))

from src.common.charts import *
from src.common import utils
from src.models.projects_info import ProjectsInfo
from src.models.tasks_info import TasksInfo


def get_projects_info():
    if st.session_state.get(constants.PROJECTS):
        return st.session_state[constants.PROJECTS]

    json_projects = utils.from_file("{\"num_count\":0,\"projects\":[]}",
                                    # os.path.join(os.getcwd(), "data"),
                                    constants.ADQ_WORKING_FOLDER,
                                    constants.PROJECTS + constants.JSON_EXT)
    return ProjectsInfo.from_json(json_projects)


def select_project(is_sidebar=True):
    projects_info = get_projects_info()
    if projects_info.num_count > 0:
        df_projects = pd.DataFrame(projects_info.to_json()[constants.PROJECTS])
        df_project_id_names = df_projects[["id", "name"]]
        options = ["{}-{}".format(project_id, name)
                   for project_id, name in df_project_id_names[["id", "name"]].values.tolist()]
        # set an empty string as the default selection - no action
        options.append("")
        if is_sidebar:
            selected_project = st.sidebar.selectbox("Select project",
                                                    options=options,
                                                    index=len(options) - 1)

        else:
            selected_project = st.selectbox("Select project",
                                            options=options,
                                            index=len(options) - 1)
        if selected_project:
            project_id, name, = selected_project.split('-', maxsplit=1)
            return projects_info.get_project_by_id(int(project_id))
    else:
        st.markdown("**No project is created!**")


def get_tasks_info():
    if st.session_state.get(constants.TASKS):
        return st.session_state[constants.TASKS]

    json_tasks = utils.from_file("{\"num_count\":0,\"tasks\":[]}",
                                 constants.ADQ_WORKING_FOLDER,
                                 constants.TASKS + constants.JSON_EXT)
    return TasksInfo.from_json(json_tasks)


def select_task(project_id):
    tasks_info = get_tasks_info()
    if tasks_info.num_count > 0:
        df_tasks = pd.DataFrame(tasks_info.to_json()[constants.TASKS])
        df_tasks = df_tasks[["id", "name", "project_id"]]
        df_filtered = df_tasks[df_tasks['project_id'] == project_id]
        options = ["{}-{}".format(task_id, name)
                   for task_id, name, project_id in
                   df_filtered[["id", "name", "project_id"]].values.tolist()]
        # set an empty string as the default selection - no action
        options.append("")
        selected_task = st.sidebar.selectbox("Select task",
                                             options=options,
                                             index=len(options) - 1)
        if selected_task:
            # Get the index of the selected option
            # Use it to get the corresponding images folder
            selected_index = options.index(selected_task)
            task_id, _ = selected_task.split('-', maxsplit=1)
            return tasks_info.get_task_by_id(int(task_id)), selected_index
    else:
        st.markdown("**No project is created!**")

    return None, None


def main():
    if not os.path.exists(constants.ADQ_WORKING_FOLDER):
        os.mkdir(constants.ADQ_WORKING_FOLDER)

    st.set_page_config(page_title="DaRT")
    st.header("**DaRT** - Data Reviewing Tool")
    st.subheader("Under Construction")
    st.image(os.path.join(os.pardir, "data", "under-construction.jpg"), use_column_width=True)

    json_projects = utils.from_file("{\"num_count\":0,\"projects\":[]}",
                                    # os.path.join(os.getcwd(), "data"),
                                    constants.ADQ_WORKING_FOLDER,
                                    constants.PROJECTS + constants.JSON_EXT)
    projects_info = ProjectsInfo.from_json(json_projects)

    st.session_state[constants.PROJECTS] = projects_info


if __name__ == '__main__':
    main()
