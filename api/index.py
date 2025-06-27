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
    
    # 添加项目信息展示页面
    @app.route('/')
    def index():
        from flask import jsonify
        return jsonify({
            'name': '企业微信群机器人',
            'version': '2.1.0',
            'description': '功能丰富的企业微信群机器人，支持定时发送每日消息',
            'features': [
                '🌤️ 天气播报 - 获取实时天气信息',
                '📅 今日运势 - 老黄历信息，包含宜忌、冲煞等',
                '😄 搞笑内容 - 每日搞笑破产文学',
                '🍽️ 午餐推荐 - 智能午餐建议',
                '⏰ 定时发送 - 工作日自动推送',
                '🤖 AI生成 - 动态开场白和智能内容'
            ],
            'api_endpoints': {
                'GET /': '项目信息和API文档',
                'POST /send': '手动发送消息',
                'POST /send-daily': '立即发送每日消息',
                'GET /preview-daily': '预览每日消息内容',
                'GET /health': '健康检查'
            },
            'status': 'running',
            'deployment': 'Vercel',
            'github': 'https://github.com/your-username/wework-ark-bot',
            'docs': 'https://github.com/your-username/wework-ark-bot/blob/main/README.md'
        })
    
except Exception as e:
    # 记录初始化错误
    init_error = str(e)
    
    # 如果导入失败，创建一个简单的Flask应用作为fallback
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    @app.route('/')
    def error_handler():
        return jsonify({
            'name': '企业微信群机器人',
            'status': 'error',
            'message': f'应用初始化失败: {init_error}',
            'troubleshooting': [
                '检查环境变量配置是否正确',
                '确认所有依赖包已正确安装',
                '查看部署日志获取详细错误信息'
            ]
        }), 500

# 导出应用供Vercel使用
# 这是Vercel期望的WSGI应用入口点