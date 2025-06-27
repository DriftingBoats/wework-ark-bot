#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 初始化错误信息
init_error = None

try:
    # 导入Flask应用和机器人实例
    from wework_bot import app, bot
    
    # 确保应用正确初始化
    if not hasattr(app, 'wsgi_app'):
        # 如果没有wsgi_app属性，说明Flask应用可能有问题
        from flask import Flask
        if not isinstance(app, Flask):
            raise TypeError("app is not a Flask instance")
    
except Exception as e:
    # 记录初始化错误
    init_error = str(e)
    
    # 如果导入失败，创建一个简单的Flask应用作为fallback
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    @app.route('/')
    def error_handler():
        return jsonify({
            'status': 'error',
            'message': f'Application initialization failed: {init_error}'
        }), 500

# 导出应用供Vercel使用
# 这是Vercel期望的WSGI应用入口点