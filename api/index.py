#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WSGI应用入口点
用于部署到生产环境
"""

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
    
    @app.route('/api/')
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
    @app.route('/api/index.html')
    def serve_index():
        from flask import send_from_directory
        import os
        # 获取项目根目录
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return send_from_directory(project_root, 'index.html')
    
    @app.route('/api/home')
    def serve_home():
        from flask import send_from_directory
        import os
        # 获取项目根目录
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return send_from_directory(project_root, 'index.html')

# 导出应用供部署使用
# WSGI应用入口点

if __name__ == '__main__':
    # 本地开发时启动服务器
    print("启动Flask开发服务器...")
    app.run(host='0.0.0.0', port=5000, debug=True)