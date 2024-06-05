from api.error import error_to_description


class MatrixError(Exception):
    def __init__(self, errcode=None, error_message=None):
        self.errcode = errcode
        self.error_message = error_message

    @classmethod
    def from_dict(cls, error_dict):
        errcode = error_dict.get('errcode', 'Unknown error code')
        error_message = error_dict.get('error', 'No error message provided')
        return cls(errcode, error_message)

    def get_error_description(self):
        return error_to_description.error_codes[self.errcode]

    def display(self):
        print(f"Error Code: {self.errcode}")
        print(f"Error Message: {self.error_message}")
