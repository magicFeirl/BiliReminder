from datetime import datetime

from app import ntfy
from app import db
import app.weibo.dynamic as wb_dyanmic
import app.bilibili.live as bili_live

import config


def push_bili(room_id: str, channel_name: str):
    jdata = db.load_db()

    live_status, username, content = bili_live.format_live_message(
        room_id=room_id)

    pre_live_status = jdata[room_id]['live_status']

    if live_status == 1 and pre_live_status != 1:
        # 开播
        ntfy.send(channel_name, **content)
    elif live_status != 1 and pre_live_status == 1:
        # 下播
        ntfy.send(channel_name, **content)

    title, message = content['headers']['Title'], content['message']
    print(title.decode('utf-8'), '\n', message.decode('utf-8'))
    print()

    jdata[room_id]['live_status'] = live_status
    jdata[room_id]['last_check'] = str(datetime.now())
    jdata[room_id]['username'] = username

    # python dict 的 key -> value 没变不会触发 __setitem__，导致数据没有更新，需要用时间戳强制触发一次
    jdata['update_time'] = str(datetime.now())


def push_weibo(user_id: str, channel_name: str):
    NAMESPACE = 'weibo'
    # 最多只发送最新的 3 条微博
    max_weibo_count = 3

    jdata = db.load_db()

    response = wb_dyanmic.get_user_dynamics(user_id)

    if response['ok'] == 1:
        cards = response['data']['cards']

        for mblog, message, ntfy_params in wb_dyanmic.parse_dyanimcs(cards):
            if not max_weibo_count:
                break

            id = mblog['id']
            # mblog.type: 2 置顶, 0 普通
            if jdata[NAMESPACE]['dynamic'].get('id', None) == True:
                continue

            jdata[NAMESPACE]['dynamic'][id] = True

            ntfy.send(name=channel_name, **ntfy_params)
            print(message)
            max_weibo_count -= 1



def main():
    for room_id in config.LIVE_ROOM_ID_LIST:
        push_bili(room_id=room_id, channel_name='ac8888')

    for weibo_user_id in config.WEIBO_USER_ID_LIST:
        push_weibo(weibo_user_id, channel_name='ac8888')


if __name__ == '__main__':
    main()
