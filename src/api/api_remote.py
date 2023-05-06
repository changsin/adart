import json
import logging

import requests

from src.models.users_info import User, UsersInfo
from .api_base import ApiBase

logger = logging.getLogger(__name__)


class ApiRemote(ApiBase):

    @staticmethod
    def send_api_request(request):
        try:
            response = requests.request(**request)
            response.raise_for_status()

            response_text = response.text
            code = response.status_code
            if code == requests.codes.ok or code == requests.codes.created:
                return True, response_text
            else:
                return False, response_text
        except requests.exceptions.RequestException as err:
            response_text = str(err)
            return False, response_text

    def get_users_info(self):
        url = f"{self.url_base}/api/v1/users/?&limit=99999"

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            json_data = json.loads(response.text)
            users = []
            for data in json_data:
                users.append(data)

            return UsersInfo.from_json({"num_count": len(users), "users": users})

        except requests.exceptions.RequestException as err:
            logger.error(f"Error: req_get_user_list_info - {err}")
            return None
