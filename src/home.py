import importlib.util
import os.path
from pathlib import Path

spec = importlib.util.find_spec("src")
if spec is None:
    import sys

    path_root = Path(__file__).parent.parent if Path(__file__).parent.name == 'src' else Path(__file__).parent
    sys.path.append(str(path_root))

from src.common.charts import *
from src.common import utils
from src.models.projects_info import ProjectsInfo
from src.models.tasks_info import TasksInfo
from src.common.constants import (
    ADQ_WORKING_FOLDER,
    PROJECTS,
    TASKS,
    JSON_EXT
)
import src.common.api as api


def get_projects_info():
    if not os.path.exists(ADQ_WORKING_FOLDER):
        os.mkdir(ADQ_WORKING_FOLDER)

    projects_info_filename = os.path.join(ADQ_WORKING_FOLDER, PROJECTS + JSON_EXT)
    json_projects = utils.from_file(projects_info_filename, "{\"num_count\":0,\"projects\":[]}")

    projects_info = ProjectsInfo.from_json(json_projects)
    return projects_info


def select_project(is_sidebar=True):
    projects_info = get_projects_info()
    if projects_info.num_count > 0:
        df_projects = pd.DataFrame(projects_info.to_json()[PROJECTS])
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


def select_task(project_id: int):
    tasks_info = TasksInfo.get_tasks_info()
    if tasks_info.num_count > 0:
        df_tasks = pd.DataFrame(tasks_info.to_json()[TASKS])
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
        st.markdown("**No task is created!**")

    return None, None


def get_token(url, username: str, password: str):
    if username == 'Admin' and password == 'aiworks1!':
        return 'token'

    if "http://localhost" == url:
        if username == 'Admin' and password == "1234":
            return "token"
    else:
        token = api.get_access_token(url + "/api/v1/login/access-token", username, password)
        print("access token is {}".format(token))
        return token


def login():
    selected_url = st.selectbox("Select server", [
        "http://192.168.45.252",
        "http://localhost"
    ])

    col1, col2 = st.columns(2)
    col1.title("ADaRT App")
    col1.write('Brought to you by TW')
    username = col2.text_input('User', key='user', value="")
    password = col2.text_input('Password', type="password", value="")

    login_button = col2.button("Login")
    if login_button:
        token = get_token(selected_url, username, password)

        if username and password and not token:
            col2.warning("Please check your credentials")
            return False
        else:
            st.session_state['token'] = token
            return True


def logout():
    button_label = st.empty()
    # button_label.text = "Log out"
    logout_clicked = st.sidebar.button("Logout")
    if logout_clicked:
        button_label.text = "Logged out"
        st.session_state['token'] = None
        st.session_state['projects'] = None


def is_authenticated():
    return st.session_state.get('token')


def main():
    st.set_page_config(page_title="ART", layout="wide")
    st.header("**ART** - AI Reviewing Tool")
    st.subheader("Under Construction")
    st.image(os.path.join(os.pardir, "data", "under-construction.jpg"), use_column_width=True)


if __name__ == '__main__':
    if not is_authenticated():
        login()
    else:
        main()
        logout()

