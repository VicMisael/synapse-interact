import argparse
import os.path

from beautifultable import BeautifulTable
import matrix_interact
from config import Config
from synapse_manager import SynapseManager
import tempfile


#  Gerência de usuários locais ok
#
#  Gerência de salas
#
#  Gerência de federações
#
#  Gerência de mídias
#
#  Estatísticas:
#
#  Mídia
#
#  Salas
#
# o Inicialmente só um programa Python para gerência via CLI
#
# o Futuramente, criar
# Exception
# Tratamento dos erros Matrix
# SSO
# Investigar Cargos KeyCloak(Gestão de Identidade)


def get_access_token():
    config = Config.from_json_file()
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        if os.path.exists(temp_file.name):
            return temp_file.read().decode()
        else:
            data = matrix_interact.get_access_token(config.base_url, config.user_name, config.password)
            token: str = data.json()['access_token']
            temp_file.write(token.encode())
            return token


def create_user(args):
    config = Config.from_json_file()
    print(args)
    manager = SynapseManager(config.base_url, get_access_token(), config.shared_secret)
    print(manager.create_user(args.username, args.password, False if args.admin is None else args.admin))


def generate_config(args):
    config = Config(args.username, args.password, args.base_url, args.shared_secret)
    config.save_to_json()


def list_users(args):
    config = Config.from_json_file()
    manager = SynapseManager(config.base_url, get_access_token(), config.shared_secret)
    users = manager.list_users()
    print_dict_list_as_table(users["users"])


def list_rooms(args):
    config = Config.from_json_file()
    manager = SynapseManager(config.base_url, get_access_token(), config.shared_secret)
    roomlist = manager.list_rooms()
    print_dict_list_as_table(roomlist)


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


def deactivate(args):
    config = Config.from_json_file()
    manager = SynapseManager(config.base_url, get_access_token(), config.shared_secret)
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


def main():
    parser = argparse.ArgumentParser(prog="SynapseInteract", epilog="Thanks for using %(prog)s! :)",
                                     description='This application is a Simple Synapse Manager CLI Interface.')
    # Create a subparsers object
    subparsers = parser.add_subparsers(help='commands', dest='command')
    subparsers.required = True  # Python 3.7 and later require setting this manually

    generate_config_parser = subparsers.add_parser('generate', help='Generate a new config file')
    generate_config_parser.add_argument('-u', '--username', required=True, help="Enter your username")
    generate_config_parser.add_argument('-p', '--password', required=True, help="Enter your password")
    generate_config_parser.add_argument('-b', '--base-url', required=True,
                                        help="Enter the base url of the synapse server")
    generate_config_parser.add_argument('-s', '--shared_secret', required=True,
                                        help="Enter your shared secret")

    generate_config_parser.set_defaults(func=generate_config)

    # Create the parser for the "create" command
    if Config.json_file_exists():
        create_parser = subparsers.add_parser('create', help='Create a new user')
        create_parser.add_argument('-u', '--username', required=True, help="Enter your username")
        create_parser.add_argument('-p', '--password', required=True, help="Enter your password")
        create_parser.add_argument("-a", "--admin", action=argparse.BooleanOptionalAction, required=False,
                                   help="Is admin?")
        create_parser.set_defaults(func=create_user)

        info_parser = subparsers.add_parser('info', help='Show user info')
        info_parser.add_argument('-u', '--username', required=True, help="Enter the username")

        info_parser.set_defaults(func=show_user_info)

        change_password = subparsers.add_parser('change_password', help='Change password')
        change_password.add_argument('-u', '--username', required=True, help="Enter the username")
        change_password.add_argument('-p', '--password', required=True, help="Enter the password")
        change_password.set_defaults(func=new_password)

        list_users_parser = subparsers.add_parser('list_users', help='Create a new user')
        list_users_parser.add_argument('-t', '--access_token', required=True, help="Enter your access Token")
        list_users_parser.set_defaults(func=list_users)

        remove_user = subparsers.add_parser('remove_user', help='Create a new user')
        remove_user.add_argument('-u', '--username', required=True, help="Enter your username")
        remove_user.add_argument("-e", "--erase", action=argparse.BooleanOptionalAction, required=False,
                                 help="Is admin?")
        remove_user.set_defaults(func=deactivate)

        # Enable user

        login = subparsers.add_parser('login',
                                      help='Generate your access token given the username and password on the config')
        login.set_defaults(func=get_access_token)

        list_room = subparsers.add_parser('list_rooms', help='List all rooms ')
        list_room.add_argument('-t', '--access_token', required=True, help="Enter your access Token")
        list_room.set_defaults(func=list_rooms)

        create_room = subparsers.add_parser('create_room', help='Create a new room')
        create_room.add_argument('-n', '--name', required=True, help="Enter the room name")
        create_room.add_argument('-p', '--preset', required=True, help="Enter the room preset")
        create_room.add_argument('-d', '--description', required=True, help="Enter the description")
        create_room.add_argument('-a', '--alias', required=True, help="Enter the alais")
        create_room.set_defaults(func=new_room)
    else:
        print("Config file not found, please generate with generate")
    args = parser.parse_args()

    args.func(args)


if __name__ == "__main__":
    main()

    # print(config.__dict__)
