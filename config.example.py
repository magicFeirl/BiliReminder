# config.example.py
# Configuration file for BiliReminder

# List of live room IDs, with associated ntfy channel name and backend push URL.
# Example:
# - id: Live room ID of the Bilibili channel
# - channel: The ntfy channel name for notifications
# - url: The ntfy backend push URL
LIVE_ROOM_ID_LIST = [
    {'id': '12345', 'channel': 'bili_live_notifications', 'url': 'https://ntfy.example.com/bili_live'},
    {'id': '67890', 'channel': 'game_stream_updates', 'url': 'https://ntfy.example.com/game_stream'},
]

# List of Weibo user IDs, with associated ntfy channel name and backend push URL.
# Example:
# - id: Weibo user ID whose updates are to be monitored
# - channel: The ntfy channel name for notifications
# - url: The ntfy backend push URL
WEIBO_USER_ID_LIST = [
    {'id': 'weibo_user_1', 'channel': 'weibo_updates', 'url': 'https://ntfy.example.com/weibo_user1'},
    {'id': 'weibo_user_2', 'channel': 'celebrity_updates', 'url': 'https://ntfy.example.com/celeb_updates'},
]
