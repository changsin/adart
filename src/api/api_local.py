import os

import src.common.utils as utils
from src.common.constants import (
    ADQ_WORKING_FOLDER,
    USERS,
    JSON_EXT
)
from src.models.users_info import UsersInfo
from .api_base import ApiBase


class ApiLocal(ApiBase):
    def get_users_info(self):
        users_filename = os.path.join(ADQ_WORKING_FOLDER, USERS + JSON_EXT)
        json_users_info = utils.from_file(users_filename, "{\"num_count\": 0, \"users\":[]}")

        return UsersInfo.from_json(json_users_info)

