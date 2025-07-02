#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目信息API模块
"""

from flask import Blueprint, jsonify
from datetime import datetime

info_bp = Blueprint('info', __name__)

@info_bp.route('/', methods=['GET'])
@info_bp.route('/info', methods=['GET'])
def get_api_info():
    """获取API信息和文档"""
    api_info = {
        'name': '企业微信群机器人 API',
        'version': '2.1.0',
        'description': '功能丰富的企业微信群机器人，支持定时发送每日消息',
        'features': [
            '🌤️ 天气播报 - 获取实时天气信息',
            '📅 今日运势 - 老黄历信息，包含宜忌、冲煞等',
            '⭐ 星座运势 - 十二星座每日运势',
            '😄 搞笑内容 - 每日搞笑破产文学',
            '🍽️ 午餐推荐 - 智能午餐建议',
            '⏰ 定时发送 - 工作日自动推送',
            '🤖 AI生成 - 动态开场白和智能内容'
        ],
        'api_endpoints': {
            'info': {
                'GET /api/': '项目信息和API文档',
                'GET /api/info': '项目信息和API文档'
            },
            'health': {
                'GET /api/health': '健康检查',
                'GET /api/status': '状态检查（兼容旧版本）'
            },
            'weather': {
                'GET /api/weather': '获取天气信息',
                'GET /api/weather/current': '获取当前天气（实况）',
                'GET /api/weather/forecast': '获取天气预报'
            },
            'fortune': {
                'GET /api/fortune': '获取老黄历信息',
                'GET /api/fortune/today': '获取今日老黄历',
                'GET /api/fortune/almanac': '获取详细的黄历信息',
                'GET /api/fortune/simple': '获取简化的老黄历信息'
            },
            'constellation': {
                'GET /api/constellation': '获取星座运势',
                'GET /api/constellation/list': '获取支持的星座列表',
                'GET /api/constellation/today': '获取今日星座运势',
                'POST /api/constellation/batch': '批量获取多个星座运势'
            },
            'message': {
                'POST /api/message/send': '发送自定义消息',
                'POST /api/message/send-daily': '发送每日消息',
                'GET /api/message/preview-daily': '预览每日消息内容',
                'POST /api/message/send-weather': '发送天气消息',
                'POST /api/message/send-fortune': '发送老黄历消息',
                'POST /api/message/send-lunch': '发送午餐推荐消息',
                'GET /api/message/templates': '获取消息模板列表'
            }
        },
        'status': 'running',
        'deployment': 'Docker',
        'timestamp': datetime.now().isoformat(),
        'github': 'https://github.com/DriftingBoats/wework-bot',
        'docs': 'https://github.com/DriftingBoats/wework-bot/blob/main/README.md'
    }
    
    return jsonify(api_info)

@info_bp.route('/version', methods=['GET'])
def get_version():
    """获取版本信息"""
    return jsonify({
        'version': '2.1.0',
        'api_version': 'v1',
        'build_date': '2024-01-01',
        'python_version': '3.8+',
        'framework': 'Flask'
    })

@info_bp.route('/endpoints', methods=['GET'])
def get_endpoints():
    """获取所有API端点列表"""
    endpoints = {
        'health_check': {
            'path': '/api/health',
            'method': 'GET',
            'description': '健康检查接口'
        },
        'weather_info': {
            'path': '/api/weather',
            'method': 'GET',
            'description': '获取天气信息',
            'parameters': {
                'city': '城市名称（可选）'
            }
        },
        'fortune_info': {
            'path': '/api/fortune',
            'method': 'GET',
            'description': '获取老黄历信息',
            'parameters': {
                'format': 'structured 或 text（可选）'
            }
        },
        'constellation_info': {
            'path': '/api/constellation',
            'method': 'GET',
            'description': '获取星座运势',
            'parameters': {
                'sign': '星座名称（必需）'
            }
        },
        'send_message': {
            'path': '/api/message/send',
            'method': 'POST',
            'description': '发送自定义消息',
            'body': {
                'message': '消息内容（必需）'
            }
        },
        'send_daily': {
            'path': '/api/message/send-daily',
            'method': 'POST',
            'description': '发送每日消息'
        },
        'preview_daily': {
            'path': '/api/message/preview-daily',
            'method': 'GET',
            'description': '预览每日消息内容'
        }
    }
    
    return jsonify({
        'success': True,
        'data': {
            'endpoints': endpoints,
            'total': len(endpoints),
            'base_url': '/api'
        }
    })

@info_bp.route('/stats', methods=['GET'])
def get_stats():
    """获取API统计信息"""
    stats = {
        'total_endpoints': 20,
        'modules': {
            'health': 2,
            'weather': 3,
            'fortune': 4,
            'constellation': 4,
            'message': 7,
            'info': 4
        },
        'features': {
            'weather_api': True,
            'fortune_api': True,
            'constellation_api': True,
            'message_sending': True,
            'ai_integration': True,
            'caching': True,
            'error_handling': True
        },
        'last_updated': datetime.now().isoformat()
    }
    
    return jsonify({
        'success': True,
        'data': stats
    })