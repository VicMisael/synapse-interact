import requests


def get_access_token(base_url, username, password):
    url = f'{base_url}/_matrix/client/r0/login'
    payload = {
        "type": "m.login.password",
        "user": username,
        "password": password
    }
    response = requests.post(url, json=payload)
    data = response.json()
    return data['access_token']


class MatrixManager:
    def __init__(self, BaseUrl, AccessToken, SharedSecret):
        self.base_url = BaseUrl
        self.access_token = AccessToken
        self.shared_secret = SharedSecret

    def get_headers(self):
        return {'Authorization': f'Bearer {self.access_token}'}

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
        print(data)
        response = requests.post(url, json=data, headers=self.get_headers())
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception("Falha ao criar salas: " + response.json().get('error', 'Erro desconhecido'))
