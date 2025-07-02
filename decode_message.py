#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

try:
    response = requests.get('http://localhost:5000/api/message/preview-daily')
    if response.status_code == 200:
        data = response.json()
        message = data.get('message', '')
        print("=" * 50)
        print("今日文案预览")
        print("=" * 50)
        print(message)
        print("=" * 50)
    else:
        print(f"请求失败，状态码: {response.status_code}")
except Exception as e:
    print(f"获取文案失败: {e}")