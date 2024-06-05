import json
import os

from api import matrix_interact
from api.error.matrix_error import MatrixException
from api.matrix_interact import whoami
from config import Config
from beautifultable import BeautifulTable
from api.synapse_manager import SynapseManager
import tempfile


def check_access_token(config: Config, access_token: str) -> bool:
    result = whoami(config.base_url, access_token)

    return result.ok

def generate_access_token(config: Config):
    response = matrix_interact.get_access_token(config.base_url, config.user_name, config.password)
    if response.ok:
        token: str = response.json()['access_token']
        return token
    raise MatrixException.from_dict(response.json())


def get_access_token(config: Config):
    tempdir = tempfile.gettempdir()
    temp_file_dir = os.path.join(tempdir, 'synapse_interact')

    os.makedirs(temp_file_dir, exist_ok=True)
    temp_file_path = os.path.join(temp_file_dir, 'access_token.json')

    if os.path.exists(temp_file_path):
        with open(temp_file_path, 'r') as temp_file:
            user_token_dict = json.load(temp_file)
            if user_token_dict['user_name'] == config.user_name and check_access_token(config, user_token_dict['access_token']):
                return user_token_dict['access_token']

    token = generate_access_token(config)
    user_token_dict = {'access_token': token, 'user_name': config.user_name}

    with open(temp_file_path, 'w') as temp_file:
        json.dump(user_token_dict, temp_file)

    return token


def create_user(args):
    config = Config.from_json_file()
    manager = SynapseManager(config.base_url, get_access_token(config), config.shared_secret)
    print(manager.create_user(args.username, args.password, False if args.admin is None else args.admin))


def generate_config(args):
    config = Config(args.username, args.password, args.base_url, args.shared_secret)
    config.save_to_json()


def whoami_action(args):
    config = Config.from_json_file()
    response = matrix_interact.whoami(config.base_url, get_access_token(config))
    if response.ok:
        print_dict_as_table(response.json())
    else:
        raise MatrixException.from_dict(response.json())


def list_users(args):
    config = Config.from_json_file()
    manager = SynapseManager(config.base_url, get_access_token(config), config.shared_secret)
    users = manager.list_users()
    print_dict_list_as_table(users["users"])


def list_rooms(args):
    config = Config.from_json_file()
    manager = SynapseManager(config.base_url, get_access_token(config), config.shared_secret)
    roomlist = manager.list_rooms()
    print_dict_list_as_table(roomlist)


def deactivate(args):
    config = Config.from_json_file()
    manager = SynapseManager(config.base_url, get_access_token(config), config.shared_secret)
    print(args)
    print(manager.deactivate_user(args.username, False if args.erase is None else args.erase))


def new_room(args):
    config = Config.from_json_file()
    manager = matrix_interact.MatrixManager(config.base_url, get_access_token(), config.shared_secret)
    print(manager.create_room(args.name, args.preset, args.alias, args.description))


def show_user_info(args):
    config = Config.from_json_file()
    manager = SynapseManager(config.base_url, get_access_token(), config.shared_secret)
    data = manager.get_userinfo(manager.get_user_id_by_displayname(args.username))
    table = BeautifulTable()
    table.columns.width = 30
    for column in data:
        table.rows.append([column, data[column]])
    print(table)


def new_password(args):
    config = Config.from_json_file()
    manager = SynapseManager(config.base_url, get_access_token(), config.shared_secret)
    user_id = manager.get_user_id_by_displayname(args.username)
    print(manager.change_password(user_id, args.password))


def print_dict_list_as_table(roomlist):
    table = BeautifulTable()
    headerCreated = False
    for room in roomlist:
        if not headerCreated:
            table.columns.header = room
            table.columns.width = 10
            headerCreated = True
        table.rows.append(room.values())
    print(table)


def print_dict_as_table(dict):
    table = BeautifulTable()
    table.columns.width = 10
    table.rows.insert(0, dict.keys())
    table.rows.insert(1, dict.values())
    print(table)
