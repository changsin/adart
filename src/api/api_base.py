from abc import ABC


class ApiBase(ABC):
    def __init__(self, url_base, token):
        self.url_base = url_base
        self.token = token

    def get_users_info(self):
        pass
