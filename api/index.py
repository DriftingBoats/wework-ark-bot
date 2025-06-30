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
            'name': '企业微信群机器人',
            'status': 'error',
            'message': f'应用初始化失败: {init_error}',
            'troubleshooting': [
                '检查环境变量配置是否正确',
                '确认所有依赖包已正确安装',
                '查看部署日志获取详细错误信息'
            ]
        }), 500
else:
    # 添加静态文件服务
    @app.route('/index.html')
    def serve_index():
        from flask import send_from_directory
        import os
        # 获取项目根目录
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return send_from_directory(project_root, 'index.html')
    
    @app.route('/home')
    def serve_home():
        from flask import send_from_directory
        import os
        # 获取项目根目录
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return send_from_directory(project_root, 'index.html')
    
    # 根路径直接显示index.html页面
    @app.route('/')
    def serve_index_root():
        from flask import send_from_directory
        import os
        # 获取项目根目录
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return send_from_directory(project_root, 'index.html')
    
    # API信息页面移到/api路径
    @app.route('/api')
    def api_index():
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
                'GET /api': '项目信息和API文档',
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

    # 添加老黄历API接口
    @app.route('/api/fortune')
    def get_fortune():
        from flask import jsonify
        try:
            fortune_data = bot.get_today_fortune_structured()
            return jsonify({
                'success': True,
                'data': fortune_data
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'获取老黄历失败: {str(e)}'
            }), 500
    
    # 添加星座运势API接口
    @app.route('/api/constellation')
    def get_constellation():
        from flask import jsonify, request
        try:
            sign = request.args.get('sign')
            if not sign:
                return jsonify({
                    'success': False,
                    'error': '请提供星座参数'
                }), 400
            
            constellation_data = bot.get_constellation_fortune_structured(sign)
            return jsonify({
                'success': True,
                'data': constellation_data
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'获取星座运势失败: {str(e)}'
            }), 500

# 导出应用供Vercel使用
# 这是Vercel期望的WSGI应用入口点

if __name__ == '__main__':
    # 本地开发时启动服务器
    print("启动Flask开发服务器...")
    app.run(host='0.0.0.0', port=5000, debug=True)