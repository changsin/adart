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


def select_project():
    projects_info = get_projects_info()
    if projects_info.num_count > 0:
        df_projects = pd.DataFrame(projects_info.to_json()[constants.PROJECTS])
        df_project_id_names = df_projects[["id", "name"]]
        options = ["{}-{}".format(project_id, name)
                   for project_id, name in df_project_id_names[["id", "name"]].values.tolist()]
        # set an empty string as the default selection - no action
        options.append("")
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


def select_task():
    tasks_info = get_tasks_info()
    if tasks_info.num_count > 0:
        df_tasks = pd.DataFrame(tasks_info.to_json()[constants.TASKS])
        df_tasks_id_names = df_tasks[["id", "name"]]
        options = ["{}-{}".format(task_id, name)
                   for task_id, name in df_tasks_id_names[["id", "name"]].values.tolist()]
        # set an empty string as the default selection - no action
        options.append("")
        selected_task = st.selectbox("Select task",
                                        options=options,
                                        index=len(options) - 1)

        if selected_task:
            task_id, name, = selected_task.split('-', maxsplit=1)
            return tasks_info.get_task_by_id(int(task_id))
    else:
        st.markdown("**No project is created!**")


def main():
    if not os.path.exists(constants.ADQ_WORKING_FOLDER):
        os.mkdir(constants.ADQ_WORKING_FOLDER)

    st.set_page_config(page_title="DaRT")
    st.header("**DaRT** - Data Reviewing Tool")
    st.subheader("Under Construction")
    st.image(os.path.join(os.pardir, "data", "under-construction.jpg"))

    json_projects = utils.from_file("{\"num_count\":0,\"projects\":[]}",
                                    # os.path.join(os.getcwd(), "data"),
                                    constants.ADQ_WORKING_FOLDER,
                                    constants.PROJECTS + constants.JSON_EXT)
    projects_info = ProjectsInfo.from_json(json_projects)

    st.session_state[constants.PROJECTS] = projects_info


if __name__ == '__main__':
    main()
