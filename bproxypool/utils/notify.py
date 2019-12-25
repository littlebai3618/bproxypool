# @Time    : 2019/6/17 1:12 PM
# @Author  : 白尚林
# @File    : notify
# @Use     : 通知方法
import datetime
import json

import requests
from urllib3 import disable_warnings

disable_warnings()

from bproxypool.core.config import FrameSettings


def ding(msg, title='', at=None):
    """
    发送钉钉报警
    :param msg: str 钉钉报警的信息
    :param at: list at 谁
    :return: None
    """
    cur_time = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    data = {
        'msgtype': 'markdown',
        "markdown": {
            "title": f"【BSpider】{title}",
            "text": f"#### 【BSpider】{title}\n{msg}\n> ###### {cur_time}"
        },
        "at": {
            "atMobiles": at,
            "isAtAll": False
        }
    }
    headers = {
        'Content-Type': 'application/json'
    }

    return requests.post(
        url=FrameSettings()['DING'],
        headers=headers,
        data=json.dumps(data),
        verify=False
    )
