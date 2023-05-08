import json
import urllib.request

import requests

from src.common.logger import get_logger
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
                logger.info(f"send_api_request returned {response_text}")
            else:
                logger.error(f"ERROR: send_api_request return {response_text}")

            return response_text
        except requests.exceptions.RequestException as err:
            logger.error(f"Error: send_api_request - {err}")
            return err

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

    def list_users(self) -> dict:
        url = f"{self.url_base}/api/v1/users/?&limit=99999"
        response_text = ApiRemote.send_api_request("GET", url, self.token)
        if response_text:
            json_data = json.loads(response_text)
            users = []
            for data in json_data:
                users.append(data)

            return {"num_count": len(users), "users": users}

    def create_user(self, new_user_dict: dict) -> dict:
        url = f"{self.url_base}/api/v1/users/"
        del new_user_dict['id']
        return ApiRemote.send_api_request_with_json_body("POST", url, self.token, new_user_dict)

    def delete_user(self, user_id: int) -> dict:
        url = f"{self.url_base}/api/v1/users/{user_id}"
        response_text = ApiRemote.send_api_request("DELETE", url, self.token)
        return json.loads(response_text)

    def list_groups(self) -> list:
        """
        :return:
         [{"name":"user","is_admin":false,"is_user":true,"is_reviewer":false,"read_only":false,"id":1},
         {"name":"reviewer","is_admin":true,"is_user":false,"is_reviewer":false,"read_only":false,"id":2},
         {"name":"inspector","is_admin":false,"is_user":false,"is_reviewer":true,"read_only":false,"id":3},
         {"name":"administrator","is_admin":false,"is_user":false,"is_reviewer":false,"read_only":true,"id":4}]
        """
        url = f"{self.url_base}/api/v1/group/?skip=0&limit=100"
        response_text = ApiRemote.send_api_request("GET", url, self.token)
        return json.loads(response_text)

    def list_projects(self, limit=100, date_start="1000-01-01", date_end="9999-12-30") -> dict:
        limit = f"limit={limit}"
        date_start = f"date_start={date_start}"
        date_end = f"date_end={date_end}"
        url = f"{self.url_base}/api/v1/project/?skip=0&{limit}&is_dir_null=false&{date_start}&{date_end}"
        response_text = ApiRemote.send_api_request("GET", url, self.token)
        return json.loads(response_text)

    def create_project(self, new_project_dict: dict) -> dict:
        url = f"{self.url_base}/api/v1/project"
        del new_project_dict['id']
        del new_project_dict['data_files']
        del new_project_dict['label_files']
        del new_project_dict['extended_properties']

        # TODO: WIP, needs to fix a few issues
        return ApiRemote.send_api_request_with_json_body("POST", url, self.token, new_project_dict)

    def list_tasks(self, limit=100) -> dict:
        limit = f"limit={limit}"
        url = f"{self.url_base}/api/v1/task/?skip=0&{limit}"
        response_text = ApiRemote.send_api_request("GET", url, self.token)
        return json.loads(response_text)

    def list_annotation_errors(self, limit=100) -> list:
        limit = f"limit={limit}"
        url = f"{self.url_base}/api/v1/annoerror/?skip=0&{limit}"
        response_text = ApiRemote.send_api_request("GET", url, self.token)
        return json.loads(response_text)

    def list_states(self, limit=100) -> list:
        limit = f"limit={limit}"
        url = f"{self.url_base}/api/v1/state/?skip=0&{limit}"
        response_text = ApiRemote.send_api_request("GET", url, self.token)
        return json.loads(response_text)

    def list_annotation_types(self, limit=100) -> list:
        limit = f"limit={limit}"
        url = f"{self.url_base}/api/v1/annotype/?skip=0&{limit}"
        response_text = ApiRemote.send_api_request("GET", url, self.token)
        return json.loads(response_text)
