import argparse

from actions import generate_config, create_user, show_user_info, new_password, list_users, deactivate, whoami_action, \
    list_rooms, new_room
from api.error.matrix_error import MatrixException
from config import Config


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
        list_users_parser.set_defaults(func=list_users)

        remove_user = subparsers.add_parser('remove_user', help='Create a new user')
        remove_user.add_argument('-u', '--username', required=True, help="Enter your username")
        remove_user.add_argument("-e", "--erase", action=argparse.BooleanOptionalAction, required=False,
                                 help="Is admin?")
        remove_user.set_defaults(func=deactivate)

        # Enable user

        whoami = subparsers.add_parser('whoami',
                                       help='Generate your access token given the username and password on the config')
        whoami.set_defaults(func=whoami_action)

        list_room = subparsers.add_parser('list_rooms', help='List all rooms ')
        list_room.set_defaults(func=list_rooms)

        create_room = subparsers.add_parser('create_room', help='Create a new room')
        create_room.add_argument('-n', '--name', required=True, help="Enter the room name")
        create_room.add_argument('-p', '--preset', required=True, help="Enter the room preset")
        create_room.add_argument('-d', '--description', required=True, help="Enter the description")
        create_room.add_argument('-a', '--alias', required=True, help="Enter the alais")
        create_room.set_defaults(func=new_room)
    else:
        print("Config file not found, please generate with generate")
    try:
        args = parser.parse_args()

        args.func(args)
    except MatrixException as e:
        print(e.get_error_description())
        print(e.endpoint)


if __name__ == "__main__":
    main()

    # print(config.__dict__)
