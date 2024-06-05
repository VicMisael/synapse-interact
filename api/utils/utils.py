def generate_bearer_header(access_token:str):
    return {'Authorization': f'Bearer {access_token}'}