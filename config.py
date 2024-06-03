import json
import os


class Config(object):
    def __init__(self, user_name:str, password:str, base_url:str, shared_secret:str):
        self.user_name = user_name
        self.password = password
        self.base_url = base_url
        self.shared_secret = shared_secret

    def save_to_json(self, file_path: str = "config.json"):
        """
        Serialize the object to a JSON string.
        """
        with open(file_path, 'w') as f:
            json.dump({
            'user_name': self.user_name,
            'password': self.password,
            'base_url': self.base_url,
            'shared_secret': self.shared_secret  # Include the new field in serialization
            },f)

    @classmethod
    def from_json_file(cls, file_path: str = "./config.json"):
        """Creates an instance of the class from a JSON file."""
        with open(file_path, 'r') as f:
            data = json.load(f)
            return cls(data['user_name'], data['password'], data['base_url'], data['shared_secret'])

    @classmethod
    def json_file_exists(cls, file_path: str = "./config.json"):
        return os.path.exists(file_path)
