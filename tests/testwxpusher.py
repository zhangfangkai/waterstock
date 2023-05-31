#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/5/30 19:38
# @Author  : zhangfangkai
# @File    : testwxpusher.py
# @Use: PyCharm
import requests

url = "https://wxpusher.zjiecode.com/api/send/message"

headers = {
    'Content-Type': 'application/json',
}

data = {
    "appToken": "AT_A4eZONT82ErGWRRXHUNLqajw9I5Istt9",
    "content": "Wxpusher祝你中秋节快乐!",
    "summary": "消息摘要",
    "contentType": 1,
    "topicIds": [],
    "uids": [
        "UID_ifN49ygBaQ6im9to4vEwdF50EBHX"
    ],
    "verifyPay": False
}

resp = requests.post(url, headers=headers, json=data)
resp_data = resp.json()
print(resp_data)
