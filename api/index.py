#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from wework_bot import app, bot

# Vercel需要的handler函数
def handler(request):
    with app.test_request_context(request.url, method=request.method, 
                                  data=request.get_data(), 
                                  headers=dict(request.headers)):
        return app.full_dispatch_request()

# 导出app供Vercel使用
app = app