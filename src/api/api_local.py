import os

import src.common.utils as utils
from src.common.constants import (
    ADQ_WORKING_FOLDER,
    JSON_EXT,
    PROJECTS,
    TASKS,
    USERS,
)
from src.models.users_info import User, UsersInfo
from src.models.projects_info import ProjectsInfo
from src.models.tasks_info import TasksInfo
from .api_base import ApiBase


class ApiLocal(ApiBase):
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

    def delete_user(self, user_id: int) -> dict:
        users_info = UsersInfo.get_users_info()
        selected_user = users_info.get_user_by_id(user_id)
        users_info.users.remove(selected_user)
        users_info.save()
        return selected_user.to_json()

    def list_groups(self) -> list:
        return [
            {"name": "user", "is_admin": False, "is_user": True, "is_reviewer": False, "read_only": False, "id": 1},
            {"name": "reviewer", "is_admin": True, "is_user": False, "is_reviewer": False, "read_only": False, "id": 2},
            {"name": "inspector", "is_admin": False, "is_user": False, "is_reviewer": True, "read_only": False, "id": 3},
            {"name": "administrator", "is_admin": False, "is_user": False, "is_reviewer": False, "read_only": True, "id": 4}
        ]

    def list_projects(self, limit=100, date_start="1000-01-01", date_end="9999-12-30") -> dict:
        if not os.path.exists(ADQ_WORKING_FOLDER):
            os.mkdir(ADQ_WORKING_FOLDER)

        projects_info_filename = os.path.join(ADQ_WORKING_FOLDER, PROJECTS + JSON_EXT)
        return utils.from_file(projects_info_filename, "{\"num_count\":0,\"projects\":[]}")

    def list_tasks(self, limit=100) -> dict:
        tasks_info_filename = os.path.join(ADQ_WORKING_FOLDER, TASKS + JSON_EXT)
        return utils.from_file(tasks_info_filename, "{\"num_count\":0,\"projects\":[]}")

    def list_annotation_errors(self, limit=100) -> list:
        return [
            {"name": "Mis-tagged", "code": "DVE_MISS", "description": None, "is_default": True, "id": 1},
            {"name": "Untagged", "code": "DVE_UNTAG", "description": None, "is_default": True, "id": 2},
            {"name": "Over-tagged", "code": "DVE_OVER", "description": None, "is_default": True, "id": 3},
            {"name": "Range_error", "code": "DVE_RANGE", "description": None, "is_default": True, "id": 4},
            {"name": "Attributes_error", "code": "DVE_ATTR", "description": None, "is_default": True, "id": 5}
        ]





