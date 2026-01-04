import re
from typing import Tuple

from app.http import get


headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'zh,en;q=0.9,zh-CN;q=0.8,ja;q=0.7',
        'cache-control': 'no-cache',
        'captcha_id': '1123',
        'captcha_output': '1123',
        # Note: Cookies are handled separately in 'requests' but included here for completeness
        # The 'Cookie' header would contain the values from the -b or --cookie option
        'gen_time': '1762607888',
        'lot_number': '4a37a7cf60e94430a1fc896f464deb16',
        'mweibo-pwa': '1',
        'pass_token': '43d2377e8be834aa4e71b62261f3fac025694310a09b643265af885145225021',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': 'https://m.weibo.cn/p/2304137618923072_-_WEIBO_SECOND_PROFILE_WEIBO',
        'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
        'x-xsrf-token': '1fcae1'
}


cookies = {
        'SUBP': '0033WrSXqPxfM725Ws9jqgMF55529P9D9W5XpuloYV5y7ZDcIWogOxe75JpX5KMhUgL.FoqE1hBEe0qceoM2dJLoIpWSqgUDqHiLqcv.eK2XSK2X',
        'SCF': 'AlIQLZ6Jlce2b3OuDnn_1jMDyGia98Oy7VoEdWkXcXRd5SOscnsIejKyOABaVrdsGQNZJK0UVEoYtOVWlbGI7pc.',
        'SUB': '_2A25ECszKDeRhGeBM41YT8yjKyTuIHXVnZkACrDV6PUJbktANLUKikW1NRK1gG4AGnQd8RLPwYD_UsF8bfjzJT-dJ',
        'ALF': '1765165466',
        'MLOGIN': '1',
        '_T_WM': '16984796439',
        'WEIBOCN_FROM': '1110006030',
        'XSRF-TOKEN': '2faa7d',
        'M_WEIBOCN_PARAMS': 'luicode%3D20000174%26launchid%3D10000360-page_H5%26uicode%3D10000011%26fid%3D2304137618923072_-_WEIBO_SECOND_PROFILE_WEIBO'
}


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

        try:
            return get(api, params=params, headers=headers, cookies=cookies)
        except Exception as e:
            print('Get weibo API failed:', e)
            print(get(api, params=params, json=False))

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
    region_name = mblog.get('region_name')
    card_id = mblog.get('id')

    pic = mblog['retweeted_status'].get('bmiddle_pic') if repost_type else mblog.get(
        'bmiddle_pic')
    pic_num = mblog['retweeted_status'].get('pic_num') if repost_type else mblog.get(
        'pic_num')
    blog_text = mblog['text'].replace('<br />', '\n')
    is_long_text = mblog.get('isLongText')
    if is_long_text:
        long_text_result = get(f'https://m.weibo.cn/statuses/extend?id={card_id}', headers=headers)['data']
        if long_text_result['ok'] == 1:
            blog_text = long_text_result['longTextContent']

    blog_text = re.sub(r'<[^>]+>', '', blog_text)

    """
    e.g.:
    xxx 发布/转发了微博

    xxxx(微博内容)

    发布于xx

    1张图片
    """
    text = f"""
          {blog_text}
          {mblog['created_at']}

          {region_name}          

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
