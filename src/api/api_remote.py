import json
import urllib.request

import requests

from src.common.logger import get_logger
from src.models.users_info import UsersInfo
from .api_base import ApiBase

logger = get_logger(__name__)


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
            logger.error(f"Error: req_get_user_list_info - {err}")
            return False, err

    @staticmethod
    def send_api_request_with_json_body(url, access_token, method, json_body):
        request = urllib.request.Request(url, method=method)
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        for key, value in headers.items():
            request.add_header(key, value)
        request.add_header('Accept', 'application/json')

        json_data = json.dumps(json_body)
        logger.info(f"json_data: {json_data}")
        data = json_data.encode("utf-8")
        request.add_header("Content-Length", str(len(data)))
        request.data = data
        with urllib.request.urlopen(request) as response:
            return response.read()

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

    def create_user(self, new_user_dict: dict) -> dict:
        url = f"{self.url_base}/api/v1/users/"

        try:
            response = ApiRemote.send_api_request_with_json_body(url, self.token, "POST", new_user_dict)
            logger.info(f"response: {response}")
            json_data = json.loads(response.text)
            logger.info(f"response json_data: {json_data}")

            return json_data

        except requests.exceptions.RequestException as err:
            logger.error(f"Error: create_user - {err}")
            return None
