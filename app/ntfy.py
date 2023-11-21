import requests


def send(name: str, message: str, headers=None):
    api = f'https://ntfy.sh/{name}'

    if not headers:
        headers = {}

    return requests.post(api,  data=message, headers=headers).json()
