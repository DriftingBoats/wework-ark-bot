#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
健康检查API模块
"""

from flask import Blueprint, jsonify
import os
from datetime import datetime

health_bp = Blueprint('health', __name__, url_prefix='/health')

@health_bp.route('/', methods=['GET'])
def health_check():
    """健康检查接口"""
    try:
        # 检查环境变量配置
        webhook_configured = bool(os.getenv('WEBHOOK_URL'))
        weather_api_configured = bool(os.getenv('WEATHER_API_KEY'))
        ark_api_configured = bool(os.getenv('ARK_API_KEY'))
        
        # 计算运行时间（简单示例）
        uptime = "运行中"
        
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'uptime': uptime,
            'services': {
                'webhook': 'configured' if webhook_configured else 'not_configured',
                'weather_api': 'configured' if weather_api_configured else 'not_configured',
                'ark_api': 'configured' if ark_api_configured else 'not_configured'
            },
            'version': '2.1.0'
        }
        
        return jsonify(health_status)
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@health_bp.route('/status', methods=['GET'])
def status_check():
    """状态检查接口（兼容旧版本）"""
    return health_check()