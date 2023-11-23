from datetime import datetime

from app import ntfy
from app import db

import app.bilibili.live as bili_live

import config


def push_bili():
    jdata = db.load_db()

    for room_id in config.LIVE_ROOM_ID_LIST:
        live_status, username, content = bili_live.format_live_message(
            room_id=room_id)
        pre_live_status = jdata[room_id]['live_status']

        if live_status == 1 and pre_live_status != 1:
            # 开播
            ntfy.send('ac8888', **content)
        elif live_status != 1 and pre_live_status == 1:
            # 下播
            ntfy.send('ac8888', **content)

        title, message = content['headers']['Title'], content['message']
        print(title.decode('utf-8'), '\n', message.decode('utf-8'))
        print()

        jdata[room_id]['live_status'] = live_status
        jdata[room_id]['last_check'] = str(datetime.now())
        jdata[room_id]['username'] = username

    # python dict 的 key -> value 没变不会触发 __setitem__，导致数据没有更新，需要用时间戳强制触发一次
    jdata['update_time'] = str(datetime.now())


if __name__ == '__main__':
    # main()
    # push_bili
    pass