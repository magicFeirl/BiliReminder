## 推送 B 站用户开播消息到 ntfy


### 准备

1. 安装 [ntfy](https://ntfy.sh/)
2. 配置想要推送的用户的直播间 ID: `vim config.py`
3. 创建订阅
4. 打开 ntfy app，添加订阅
5. `python main.py` 执行推送；推荐使用 crontab 以定时任务的方式运行本脚本
