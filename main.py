from datetime import datetime

import requests

import pytz

from app import ntfy
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

    master_info_resp = get_room_master_info(uid)
    user_info = master_info_resp['data']['info']
    username = user_info['uname']

    now = datetime.now(tz=pytz.timezone('Asia/Shanghai'))
    message = f'{title}\n直播状态:{LIVE_STATUS_DICT[live_status]}\n时间(UTC+8) {now}'.encode(
        'utf-8')

    return {
        'message': message,
        'headers': {
            'Title': f'{username}开播了'.encode(),
            'Attach': user_cover,
            'Tags': 'loudspeaker'
        }
    }


def main():
    for room_id in config.LIVE_ROOM_ID_LIST:
        content = format_live_message(room_id=room_id)
        ntfy.send('ac8888', **content)
        print(content)


main()
