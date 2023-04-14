import urllib.parse
import urllib.request
import json


def get_access_token(login_url, username, password):
    try:
        param = urllib.parse.urlencode({'username': username, 'password': password})
        param = param.encode('utf-8')

        request = urllib.request.Request(login_url, param, method='POST')
        print("request: {} {} {}".format(request, login_url, param))

        with urllib.request.urlopen(request) as response:
            response = response.read().decode('utf-8')
            print(response)

            ret_code = response.getcode()
            if ret_code == 200:
                json_response = json.loads(response)
                return json_response['access_token']
    except urllib.error.HTTPError as e:
        print('Error : get_access_token() - HTTPError {}'.format(e))
    except Exception as e:
        print('Error : get_access_token() - {0}'.format(e))
