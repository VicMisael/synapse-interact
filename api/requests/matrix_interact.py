import requests
from requests import Response

from api.utils import utils


def get_access_token(base_url, username, password):
    url = f'{base_url}/_matrix/client/r0/login'
    payload = {
        "type": "m.login.password",
        "user": username,
        "password": password
    }
    return requests.post(url, json=payload)


def whoami(base_url, access_token) -> Response:
    url = f'{base_url}/_matrix/client/v3/account/whoami'
    return requests.get(url, headers=utils.generate_bearer_header(access_token))


class MatrixManager:
    def __init__(self, base_url, access_token, shared_secret):
        self.base_url = base_url
        self.access_token = access_token
        self.shared_secret = shared_secret

    def create_room(self, name, preset, room_alias_name, topic):
        data = {
            "creation_content": {
                "m.federate": False
            },
            "name": name,
            "preset": preset,
            "room_alias_name": room_alias_name,
            "topic": topic
        }
        url = f'{self.base_url}/_matrix/client/v3/createRoom'
        response = requests.post(url, json=data, headers=utils.generate_bearer_header(self.access_token))
        return response
