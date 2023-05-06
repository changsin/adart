import importlib.util
import json
import os
import urllib.parse
import urllib.request
from abc import ABC

import attr

spec = importlib.util.find_spec("src")
if spec is None:
    import sys
    from pathlib import Path

    path_root = Path(__file__).parents[2]
    sys.path.append(str(path_root))

from src.api.security import decode_token


def get_access_token(login_url, username, password):
    try:
        param = urllib.parse.urlencode({'username': username, 'password': password})
        param = param.encode('utf-8')

        request = urllib.request.Request(login_url, param, method='POST')
        print("request: {} {} {}".format(request.data, login_url, param))

        with urllib.request.urlopen(request) as response:
            ret_code = response.getcode()
            if ret_code == 200:
                response = response.read().decode('utf-8')
                print(response)

                json_response = json.loads(response)

                print(decode_token(json_response['access_token']))

                return json_response['access_token']
    except urllib.error.HTTPError as e:
        print('Error : get_access_token() - HTTPError {}'.format(e))
    except Exception as e:
        print('Error : get_access_token() - {0}'.format(e))


if __name__ == '__main__':
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2ODIyMjYxMjksInN1YiI6IjIifQ.ASsV-z2NUCm5T-BHBaBzxkJHRsc5zUt7XPEjhhT-ip0"
    # token = create_access_token("test")
    decode_token(token)
