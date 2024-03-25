import requests


def get(url, params=None, json=True, **kwargs):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        **kwargs.pop('headers', {})
    }

    r = requests.get(url, params=params, headers=headers, **kwargs)

    return r.json() if json else r.text
