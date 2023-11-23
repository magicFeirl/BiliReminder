import time

from app.db import load_db
from app.ntfy import send
import app.weibo.dynamic as wb


NAMESPACE = 'weibo'

jdata = load_db()

response = wb.get_user_dynamics('7618923072')

if response['ok'] == 1:
    cards = response['data']['cards']

    for mblog, message, ntfy_params in wb.parse_dyanimcs(cards):
        id = mblog['id']

        if jdata[NAMESPACE]['dynamic'][id] == True:
            break
        
        jdata[NAMESPACE]['dynamic'][id] = True

        send(name='ac8888', **ntfy_params)
        print(message)
        time.sleep(1)
