DEFAULT_CHANNEL = "ac8888"
DEFAULT_URL = "https://ntfy.sh/"


def create_config(id: str, channel="", url=""):
    return {
        "id": id,
        "channel": channel or DEFAULT_CHANNEL,
        "url": url or DEFAULT_URL
    }


LIVE_ROOM_ID_LIST = [
    create_config(22603245, 'AceTaffy', 'http://166.1.173.17:9999/'),
    create_config(1529602),
    create_config(697),
]


WEIBO_USER_ID_LIST = [
    create_config('7618923072', 'AceTaffy', 'http://166.1.173.17:9999/')
]


AUTH_TOKEN = ''
