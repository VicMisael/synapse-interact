import argparse

import config
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

def create_user(args):
    print(f"Creating user with username: {args.username} and password: {args.password},admin {args.admin}")


def generate_config(args):
    config = Config(args.username, args.password, args.base_url, args.shared_secret)
    config.save_to_json()


def list_users(args):
    pass


def main():
    print("Synapse Interact")
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
    create_parser = subparsers.add_parser('create', help='Create a new user')
    create_parser.add_argument('-u', '--username', required=True, help="Enter your username")
    create_parser.add_argument('-p', '--password', required=True, help="Enter your password")
    create_parser.add_argument("-a", "--admin", action=argparse.BooleanOptionalAction, required=False, help="Is admin?")
    create_parser.set_defaults(func=create_user)

    list_users_parser = subparsers.add_parser('listusers', help='Create a new user')
    list_users_parser.set_defaults(func=list_users)

    deactivate_user = subparsers.add_parser('deactivateuser', help='Deactivate an user')
    deactivate_user.add_argument('-id', '--identifier', required=True, help="Enter the user id")
    deactivate_user.set_defaults(func=deactivate_user)

    args = parser.parse_args()

    args.func(args)


if __name__ == "__main__":
    main()
    config = config.Config.from_json_file()
    # print(config.__dict__)
