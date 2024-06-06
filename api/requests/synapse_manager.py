import requests
import hmac
import hashlib
import json

from api.error.matrix_error import MatrixException


class SynapseManager:
    def __init__(self, BaseUrl, AccessToken, SharedSecret):
        self.base_url = BaseUrl
        self.access_token = AccessToken
        self.shared_secret = SharedSecret

    def get_headers(self):
        return {'Authorization': f'Bearer {self.access_token}'}

    def get_nonce(self):
        url = f"{self.base_url}/_synapse/admin/v1/register"
        headers = self.get_headers()
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get('nonce')
        else:
            raise Exception("Não foi possível obter o nonce: " + response.json().get('error', 'Erro desconhecido'))

    def generate_mac(self, nonce, username, password, admin):
        key = self.shared_secret.encode()
        msg = f"{nonce}\0{username}\0{password}\0{'admin' if admin else 'notadmin'}".encode()
        return hmac.new(key, msg, hashlib.sha1).hexdigest()

    def create_user(self, username, password, admin=False):
        nonce = self.get_nonce()
        mac = self.generate_mac(nonce, username, password, admin)
        url = f"{self.base_url}/_synapse/admin/v1/register"
        data = {
            "nonce": nonce,
            "username": username,
            "password": password,
            "admin": admin,
            "mac": mac
        }
        return requests.post(url, headers=self.get_headers(), json=data)

    def get_userinfo(self, userid):
        url = f"{self.base_url}/_synapse/admin/v2/users/{userid}"
        headers = self.get_headers()
        response = requests.get(url, headers=headers)
        return response

    def get_user_id_by_displayname(self, displayname):
        url = f"{self.base_url}/_synapse/admin/v2/users"
        headers = self.get_headers()
        params = {'name': displayname}
        response = requests.get(url, headers=headers, params=params)
        if response.ok:
            users = response.json().get('users', [])
            for user in users:
                if user.get('displayname', '').lower() == displayname.lower():
                    return user['name']
            return None
        else:
            raise MatrixException.from_dict(response.json())

    def deactivate_user(self, displayname, erase: bool):
        user_id = self.get_user_id_by_displayname(displayname)
        print(f"User ID: {user_id}")
        if not user_id:
            return "Usuário não encontrado."

        url = f"{self.base_url}/_synapse/admin/v1/deactivate/{user_id}"
        headers = self.get_headers()
        data = {'erase': erase}
        response = requests.post(url, headers=headers, json=data)
        return response

    def list_users(self):
        url = f"{self.base_url}/_synapse/admin/v2/users"
        headers = self.get_headers()
        response = requests.get(url, headers=headers)
        return response

    def list_rooms(self):
        url = f"{self.base_url}/_synapse/admin/v1/rooms"
        headers = self.get_headers()
        response = requests.get(url, headers=headers)
        return response

    def change_password(self, user_id, new_password):
        url = f"{self.base_url}/_synapse/admin/v1/reset_password/{user_id}"
        headers = self.get_headers()
        data = {
            "new_password": new_password
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return "Senha alterada com sucesso."
        else:
            raise Exception("Falha ao alterar senha: " + response.json().get('error', 'Erro desconhecido'))