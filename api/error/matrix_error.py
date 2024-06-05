from api.error import error_to_description


class MatrixException(Exception):
    def __init__(self, errcode=None, error_message=None, endpoint=None):
        self.errcode = errcode
        self.error_message = error_message
        self.endpoint = endpoint

    @classmethod
    def from_dict(cls, error_dict, endpoint=None):
        errcode = error_dict.get('errcode', 'Unknown error code')
        error_message = error_dict.get('error', 'No error message provided')
        return cls(errcode, error_message)

    def get_error_description(self):
        if  self.errcode in error_to_description.error_codes.keys():
            return error_to_description.error_codes[self.errcode]
        return str(self.__dict__)

    def display(self):
        print(f"Error Code: {self.errcode}")
        print(f"Error Message: {self.error_message}")
