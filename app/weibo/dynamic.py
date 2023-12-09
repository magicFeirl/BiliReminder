import re
from typing import Tuple

from app.http import get


def get_user_dynamics(uid: str, containerid: str = None):
    """
    只提供了首页（第一页）查找，多页爬虫暂时用不到
    """
    def get_dynamics(uid: str, containerid: str = None):
        api = 'https://m.weibo.cn/api/container/getIndex'

        params = {
            'jumpfrom': 'weibocom',
            'type': 'uid',
            'value': uid,
            'containerid': containerid,
        }

        return get(api, params=params)

    # 没传 containerid，发一次不带 id 的请求获取 id
    if containerid is None:
        resp = get_dynamics(uid)
        tabs = resp['data']['tabsInfo']['tabs']

        for tab in tabs:
            if tab['tabKey'] == 'weibo':
                containerid = tab['containerid']

    if containerid:
        return get_dynamics(uid, containerid)


def parse_dyanimc(card: object) -> Tuple[object, str, object]:
    """
    :returns: [微博卡片 JSON, 消息文本, ntfy 消息对象]
    """
    if not card.get('mblog'):
        return [None] * 3

    mblog = card['mblog']
    # 有值则代表是转发
    repost_type = mblog.get('repost_type')
    action_type = '转发' if repost_type else '发布'
    tags = 'link' if repost_type else 'writing_hand'

    card_id = mblog.get('id')

    pic = mblog['retweeted_status'].get('bmiddle_pic') if repost_type else mblog.get(
        'bmiddle_pic')
    pic_num = mblog['retweeted_status'].get('pic_num') if repost_type else mblog.get(
        'pic_num')
    blog_text = mblog['text'].replace('<br />', '\n')

    """
    e.g.:
    xxx 发布/转发了微博

    xxxx(微博内容)

    1张图片
    """
    text = f"""
          {blog_text}
          {mblog['created_at']}
          
          {str(pic_num) + "张图片" if pic else ""}
      """

    title = f"{mblog['user']['screen_name']} {action_type}了微博"
    text = re.sub(r'\n\s+', '\n', text)
    # 去掉微博文本里面的 html 代码
    text = re.sub(r'<.+?>(.+?)</.+?>', r'\g<1>', text)

    return mblog, f'{title}\n{text}', {
        'message': text.encode(),
        "headers": {
            'Title': title.encode(),
            'Attach': pic if pic else "",
            'Tags': tags,
            'Action': f'view, 看!, https://m.weibo.cn/detail/{card_id}'.encode()
        }
    }


def parse_dyanimcs(cards: list):
    for card in cards:
        # 目测 card_type == 9 的是博主动态
        if card['card_type'] != 9:
            continue

        yield parse_dyanimc(card)
