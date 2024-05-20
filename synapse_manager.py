import requests
import hmac
import hashlib

class SynapseManager:
    def __init__(self,BaseUrl,AccessToken,SharedSecret):
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
        response = requests.post(url, headers=self.get_headers(), json=data)
        if response.status_code == 200:
            return "Usuário criado com sucesso."
        else:
            raise Exception("Falha ao criar usuário: " + response.json().get('error', 'Erro desconhecido'))

    def get_user_id_by_displayname(self, displayname):
        url = f"{self.base_url}/_synapse/admin/v2/users"
        headers = self.get_headers()
        params = {'name': displayname}
        response = requests.get(url, headers=headers, params=params)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        if response.status_code == 200:
            users = response.json().get('users', [])
            for user in users:
                if user.get('displayname', '').lower() == displayname.lower():
                    return user['name']
            return None
        else:
            raise Exception(f"Erro ao buscar usuários: {response.text}")

    def deactivate_user(self, displayname):
        user_id = self.get_user_id_by_displayname(displayname)
        print(f"User ID: {user_id}")
        if not user_id:
            return "Usuário não encontrado."

        confirm = input(f"Você tem certeza que deseja desativar a conta do usuário {displayname}? (s/n): ")
        if confirm.lower() != 's':
            return "Operação cancelada."

        url = f"{self.base_url}/_synapse/admin/v1/deactivate/{user_id}"
        headers = self.get_headers()
        data = {'erase': True}
        response = requests.post(url, headers=headers, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code in [200, 201]:
            return "Usuário desativado com sucesso."
        else:
            error_msg = response.json().get('error', 'Erro desconhecido ao desativar usuário')
            raise Exception(f"Falha ao desativar usuário: {error_msg}")

    def list_users(self):
        url = f"{self.base_url}/_synapse/admin/v2/users"
        headers = self.get_headers()
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception("Falha ao listar usuários: " + response.json().get('error', 'Erro desconhecido'))

    def list_quick_users(self):
        url = f"{self.base_url}/_synapse/admin/v2/users"
        headers = self.get_headers()
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            users = response.json().get('users', [])
            quick_list = [{'username': user['name'], 'displayname': user.get('displayname', 'N/A')} for user in users]
            return quick_list
        else:
            raise Exception("Falha ao listar usuários: " + response.json().get('error', 'Erro desconhecido'))

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

    def test_login(self, username, password):
        url = 'http://localhost:8008/_matrix/client/r0/login'
        payload = {
            "type": "m.login.password",
            "user": username,
            "password": password
        }
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return "Login bem-sucedido.", response.json(), response.status_code
        elif response.status_code == 403:
            return "Senha incorreta.", response.json(), response.status_code
        elif response.status_code == 404:
            return "Usuário não encontrado.", response.json(), response.status_code
        else:
            return "Falha no login.", response.json(), response.status_code