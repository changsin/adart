import json
import urllib.request

import requests

from src.common.logger import get_logger
from src.models.users_info import UsersInfo
from .api_base import ApiBase

logger = get_logger(__name__)


class ApiRemote(ApiBase):

    @staticmethod
    def send_api_request(method: str, url: str, token: str):
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
        }

        try:
            response = requests.request(method, url, headers=headers)
            response.raise_for_status()

            response_text = response.text
            code = response.status_code
            if code == requests.codes.ok or code == requests.codes.created:
                logger.info(f"send_api_request return {response}")
            else:
                logger.error(f"ERROR: send_api_request return {response}")

            return response_text
        except requests.exceptions.RequestException as err:
            logger.error(f"Error: req_get_user_list_info - {err}")
            return False, err

    @staticmethod
    def send_api_request_with_json_body(method: str, url: str, token: str, json_body: dict) -> dict:
        request = urllib.request.Request(url, method=method)
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        for key, value in headers.items():
            request.add_header(key, value)
        request.add_header('Accept', 'application/json')

        json_data = json.dumps(json_body)
        logger.info(f"json_data: {json_data}")
        data = json_data.encode("utf-8")
        request.add_header("Content-Length", str(len(data)))
        request.data = data

        try:
            with urllib.request.urlopen(request) as response:
                return response.read()
        except requests.exceptions.RequestException as err:
            logger.error(f"Error: create_user - {err}")
        except Exception as e:
            logger.error(f"Error: create_user - {e}")

    def get_users_info(self) -> dict:
        url = f"{self.url_base}/api/v1/users/?&limit=99999"
        response_text = ApiRemote.send_api_request("GET", url, self.token)
        json_data = json.loads(response_text)
        users = []
        for data in json_data:
            users.append(data)

        return {"num_count": len(users), "users": users}

    def create_user(self, new_user_dict: dict) -> dict:
        url = f"{self.url_base}/api/v1/users/"
        return ApiRemote.send_api_request_with_json_body("POST", url, self.token, new_user_dict)

    def delete_user(self, user_id: int) -> dict:
        url = f"{self.url_base}/api/v1/users/{user_id}"
        response_text = ApiRemote.send_api_request("DELETE", url, self.token)
        return json.loads(response_text)
