import json
import urllib.parse
import urllib.request
from abc import ABC

from src.api.security import decode_token
from src.common.logger import get_logger

logger = get_logger(__name__)


class ApiBase(ABC):
    def __init__(self, url_base, token):
        self.url_base = url_base
        self.token = token

    def list_users(self) -> dict:
        raise "ERROR: The parent method should not be called directly"

    def create_user(self, new_user_dict: dict) -> dict:
        raise "ERROR: The parent method should not be called directly"

    def get_user_by_email(self, email) -> dict:
        raise "ERROR: The parent method should not be called directly"

    def delete_user(self, user_id: int) -> dict:
        raise "ERROR: The parent method should not be called directly"

    def list_groups(self) -> list:
        raise "ERROR: The parent method should not be called directly"

    def list_project_pointers(self) -> dict:
        raise "ERROR: The parent method should not be called directly"

    def list_projects(self, limit=100, date_start="1000-01-01", date_end="9999-12-30") -> dict:
        raise "ERROR: The parent method should not be called directly"

    def create_project(self, new_project: dict) -> list:
        raise "ERROR: The parent method should not be called directly"

    def update_project(self, project: dict) -> list:
        raise "ERROR: The parent method should not be called directly"

    def list_task_pointers(self, project_id: int = -1) -> dict:
        raise "ERROR: The parent method should not be called directly"

    def list_tasks(self, limit=100) -> dict:
        raise "ERROR: The parent method should not be called directly"

    def create_task(self, new_task_dict: dict) -> dict:
        raise "ERROR: The parent method should not be called directly"

    def delete_task(self, task_id: int) -> dict:
        raise "ERROR: The parent method should not be called directly"

    def list_annotation_errors(self, limit=100) -> list:
        raise "ERROR: The parent method should not be called directly"

    def list_states(self, limit=100) -> list:
        raise "ERROR: The parent method should not be called directly"

    def list_annotation_types(self, limit=100) -> list:
        raise "ERROR: The parent method should not be called directly"


def get_access_token(login_url, username, password):
    try:
        param = urllib.parse.urlencode({'username': username, 'password': password})
        param = param.encode('utf-8')

        request = urllib.request.Request(login_url, param, method='POST')
        logger.info("request: {} {} {}".format(request.data, login_url, param))

        with urllib.request.urlopen(request) as response:
            ret_code = response.getcode()
            if ret_code == 200:
                response = response.read().decode('utf-8')

                logger.info(response)
                json_response = json.loads(response)
                logger.info(decode_token(json_response['access_token']))

                return json_response['access_token']
    except urllib.error.HTTPError as e:
        logger.error(f"Error : get_access_token() - HTTPError {e}")
    except Exception as e:
        logger.error(f"Error : get_access_token() - {e}")


if __name__ == '__main__':
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2ODIyMjYxMjksInN1YiI6IjIifQ.ASsV-z2NUCm5T-BHBaBzxkJHRsc5zUt7XPEjhhT-ip0"
    # token = create_access_token("test")
    decode_token(token)
