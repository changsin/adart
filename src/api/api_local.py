import os
from datetime import timedelta

import src.common.utils as utils
from src.common.constants import (
    ADQ_WORKING_FOLDER,
    JSON_EXT,
    PROJECTS,
    TASKS,
    UserType,
    USERS,
)
from src.common.logger import get_logger
from src.models.projects_info import Project, ProjectPointers
from src.models.tasks_info import Task, TaskPointers
from src.models.users_info import User, UsersInfo

from .api_base import ApiBase
from .security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    get_password_hash,
    verify_password,
)

logger = get_logger(__name__)


class ApiLocal(ApiBase):
    @staticmethod
    def get_access_token(login_url, username, password) -> str:
        api_local = ApiLocal(login_url, None)

        users_filename = os.path.join(ADQ_WORKING_FOLDER, USERS + JSON_EXT)
        if not os.path.exists(users_filename):
            super_user = User(id=0,
                              email=username,
                              full_name=username,
                              is_active=True,
                              group_id=UserType.ADMINISTRATOR.value,
                              is_superuser=True)
            new_user_dict = super_user.to_json()
            new_user_dict['password'] = get_password_hash(password)
            response = api_local.create_user(new_user_dict)
            if response:
                logger.info(f"Super user ({username}) created")
            else:
                logger.warning(f"Create user {username}) failed with {response}")

        user_dict = api_local.get_user_by_email(username)

        if user_dict and user_dict.get("email") == username:
            hashed_password = get_password_hash(password)
            stored_password_hash = user_dict["password"]
            logger.info(f"hashed_password: {hashed_password} {stored_password_hash}")
            if verify_password(password, stored_password_hash):
                access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                token = create_access_token(username, access_token_expires)
                api_local.token = token
                logger.info(f"access_token: {token}")
                return token

    def list_users(self) -> dict:
        users_filename = os.path.join(ADQ_WORKING_FOLDER, USERS + JSON_EXT)
        users_info_dict = utils.from_file(users_filename, "{\"num_count\": 0, \"users\":[]}")

        return users_info_dict

    def create_user(self, new_user_dict: dict) -> dict:
        users_info = UsersInfo.get_users_info()
        new_user = User.from_json(new_user_dict)
        new_user.id = users_info.get_next_user_id()
        users_info.add(new_user)
        users_info.save()
        return new_user_dict

    def get_user_by_email(self, email) -> dict:
        users_info = UsersInfo.get_users_info()
        if users_info.num_count > 0:
            current_user = users_info.get_user_by_email(email)
            if current_user:
                return current_user.to_json()

    def delete_user(self, user_id: int) -> dict:
        users_info = UsersInfo.get_users_info()
        selected_user = users_info.get_user_by_id(user_id)
        users_info.users.remove(selected_user)
        users_info.num_count = len(users_info.users)
        users_info.save()
        return selected_user.to_json()

    def list_groups(self) -> list:
        return [
            {"name": "user", "is_admin": False, "is_user": True, "is_reviewer": False, "read_only": False, "id": 1},
            {"name": "reviewer", "is_admin": True, "is_user": False, "is_reviewer": False, "read_only": False, "id": 2},
            {"name": "inspector", "is_admin": False, "is_user": False, "is_reviewer": True, "read_only": False, "id": 3},
            {"name": "administrator", "is_admin": False, "is_user": False, "is_reviewer": False, "read_only": True, "id": 4}
        ]

    def list_project_pointers(self) -> dict:
        if not os.path.exists(ADQ_WORKING_FOLDER):
            os.mkdir(ADQ_WORKING_FOLDER)

        projects_filename = os.path.join(ADQ_WORKING_FOLDER, PROJECTS + JSON_EXT)
        return utils.from_file(projects_filename, "{\"project_pointers\":[]}")

    def list_projects(self, limit=100, date_start="1000-01-01", date_end="9999-12-30") -> dict:
        project_pointers_dict = self.list_project_pointers()
        projects = []
        if len(project_pointers_dict["project_pointers"]) > 0:
            project_pointers = ProjectPointers.from_json(project_pointers_dict)
            for project_pointer in project_pointers.project_pointers:
                project = ProjectPointers.load(project_pointer.id)
                projects.append(project.to_json())

        return {"num_count": len(projects), "projects": projects}

    def create_project(self, new_project_dict: dict) -> dict:
        project_pointers = ProjectPointers.from_json(self.list_project_pointers())
        new_project = Project.from_json(new_project_dict)
        new_project.id = project_pointers.get_next_project_id()
        project_pointers.add(new_project)
        project_pointers.save()
        new_project.save()
        return new_project_dict

    def update_project(self, project_dict: dict) -> dict:
        project_pointers = ProjectPointers.from_json(self.list_project_pointers())
        project_to_update = project_pointers.get_project_by_id(project_dict["id"])
        project_to_update.name = project_dict["name"]
        project_to_update.description = project_dict["description"]
        project_to_update.save()
        project_pointers.update_project(project_to_update)
        return project_dict

    def list_task_pointers(self, project_id: int = -1) -> dict:
        tasks_filename = os.path.join(ADQ_WORKING_FOLDER, TASKS + JSON_EXT)
        task_pointers = utils.from_file(tasks_filename, "{\"task_pointers\":[]}")
        if len(task_pointers["task_pointers"]) > 0 and project_id != -1:
            project_tasks = list(filter(lambda task_pointer: task_pointer["project_id"] == project_id,
                                        task_pointers["task_pointers"]))
            return {"task_pointers": project_tasks}
        return task_pointers

    def list_tasks(self, limit=100) -> dict:
        task_pointers = TaskPointers.from_json(self.list_task_pointers())
        tasks = []
        if len(task_pointers.task_pointers) > 0:
            for task_pointer in task_pointers.task_pointers:
                tasks.append(task_pointers.load(task_pointer.id).to_json())

        return {"num_count": len(tasks), "tasks": tasks}

    def create_task(self, new_task_dict: dict) -> dict:
        task_pointers = TaskPointers.from_json(self.list_task_pointers())

        new_task = Task.from_json(new_task_dict)
        new_task.id = task_pointers.get_next_task_id()
        task_pointers.add(new_task)
        task_pointers.save()
        new_task.save()
        return new_task.to_json()

    def delete_task(self, task_id: int) -> dict:
        task_pointers = TaskPointers.from_json(self.list_task_pointers())

        for task_pointer in task_pointers.task_pointers:
            if task_pointer.id == task_id:
                task_filename = os.path.join(task_pointer.dir_name, f"task-{task_id}.json")
                os.remove(task_filename)

                task_pointers.task_pointers.remove(task_pointer)
        task_pointers.save()

        return task_pointers.to_json()

    def list_annotation_errors(self, limit=100) -> list:
        return [
            {"name": "Mis-tagged", "code": "DVE_MISS", "description": None, "is_default": True, "id": 1},
            {"name": "Untagged", "code": "DVE_UNTAG", "description": None, "is_default": True, "id": 2},
            {"name": "Over-tagged", "code": "DVE_OVER", "description": None, "is_default": True, "id": 3},
            {"name": "Range_error", "code": "DVE_RANGE", "description": None, "is_default": True, "id": 4},
            {"name": "Attributes_error", "code": "DVE_ATTR", "description": None, "is_default": True, "id": 5}
        ]

    def list_states(self, limit=100) -> list:
        return [
            {"name": "New", "code": "DVS_NEW", "id": 1},
            {"name": "Working", "code": "DVS_WORKING", "id": 2},
            {"name": "Done", "code": "DVS_DONE", "id": 3},
            {"name": "Closed", "code": "DVS_CLOSED", "id": 4}
        ]

    def list_annotation_types(self, limit=100) -> list:
        return [
            {"name": "Bounding Box", "id": 1},
            {"name": "Polygon", "id": 2},
            {"name": "Polyline", "id": 3},
            {"name": "Point", "id": 4},
            {"name": "Keypoint", "id": 5},
            {"name": "Cuboid", "id": 6},
            {"name": "Spline", "id": 7},
        ]
