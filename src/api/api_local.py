import os

import src.common.utils as utils
from src.common.constants import (
    ADQ_WORKING_FOLDER,
    USERS,
    JSON_EXT
)
from src.models.users_info import User, UsersInfo
from .api_base import ApiBase


class ApiLocal(ApiBase):
    def get_users_info(self) -> dict:
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



