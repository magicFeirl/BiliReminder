import re
from datetime import datetime
from string import Template

import requests
import pytz

from app import ntfy
from app import db

import config


def get(url, params, json=True, **kwargs):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        **kwargs.pop('headers', {})
    }

    r = requests.get(url, params=params, headers=headers, **kwargs)

    return r.json() if json else r


def get_room_master_info(uid: str):
    api = 'https://api.live.bilibili.com/live_user/v1/Master/info'

    return get(api, params={'uid': uid})


def get_room_info(room_id: str):
    api = 'https://api.live.bilibili.com/room/v1/Room/get_info'

    return get(api, params={'room_id': room_id})


def format_live_message(room_id: str):
    LIVE_STATUS_DICT = {
        0: '未开播',
        1: '直播中',
        2: '轮播中'
    }

    resp = get_room_info(room_id)

    if resp['code'] != 0:
        return

    room_info = resp['data']

    uid = room_info.get('uid')
    title = room_info.get('title')
    user_cover = room_info.get('user_cover')
    live_status = room_info.get('live_status')
    live_time = room_info.get('live_time')
    if live_time[:4] != '0000':
        minutes = (datetime.now() - datetime.strptime(live_time, '%Y-%m-%d %H:%M:%S')).total_seconds() / 60
    else:
        minutes = 0

    minutes = round(minutes)
    
    master_info_resp = get_room_master_info(uid)
    user_info = master_info_resp['data']['info']
    username = user_info['uname']

    message = Template('''
        $title 
        开播时间 $live_time

        $minutes 分钟前
    ''').substitute(title=title, live_time=live_time, minutes=minutes)

    message = re.sub(r'\n\s+(.)', r'\n\g<1>', message.strip())

    return live_status, username, {
        'message': message.encode(),
        'headers': {
            'Title': f'{username}开播了'.encode(),
            'Attach': user_cover,
            'Tags': 'loudspeaker'
        }
    }


def main():
    jdata = db.load_db()

    for room_id in config.LIVE_ROOM_ID_LIST:
        live_status, username, content = format_live_message(room_id=room_id)
        pre_live_status = jdata[room_id]['live_status']
        
        if live_status == 1 and pre_live_status != 1:
            ntfy.send('ac8888', **content)
            title, message = content['headers']['Title'], content['message']
            print(title.decode('utf-8'), '\n', message.decode('utf-8'))


        jdata[room_id]['live_status'] = live_status
        jdata[room_id]['last_check'] = str(datetime.now())
        jdata[room_id]['username'] = username

    # python dict 的 key -> value 没变不会触发 __setitem__，导致数据没有更新，需要用时间戳强制触发一次
    jdata['update_time'] = str(datetime.now())


main()
