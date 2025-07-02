#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
消息发送API模块
"""

from flask import Blueprint, jsonify, request
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

message_bp = Blueprint('message', __name__, url_prefix='/message')

@message_bp.route('/send', methods=['POST'])
def send_message():
    """发送自定义消息"""
    try:
        from wework_bot import bot
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '请提供消息内容'
            }), 400
        
        message = data.get('message')
        if not message:
            return jsonify({
                'success': False,
                'error': '消息内容不能为空'
            }), 400
        
        # 发送消息
        result = bot.send_message(message)
        
        if result:
            return jsonify({
                'success': True,
                'message': '消息发送成功',
                'data': {
                    'sent_message': message
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': '消息发送失败'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'发送消息失败: {str(e)}'
        }), 500

@message_bp.route('/send-daily', methods=['POST'])
def send_daily_message():
    """发送每日消息"""
    try:
        from wework_bot import bot
        
        # 生成并发送每日消息
        result = bot.send_daily_message()
        
        if result:
            return jsonify({
                'success': True,
                'message': '每日消息发送成功'
            })
        else:
            return jsonify({
                'success': False,
                'error': '每日消息发送失败'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'发送每日消息失败: {str(e)}'
        }), 500

@message_bp.route('/preview-daily', methods=['GET'])
def preview_daily_message():
    """预览每日消息内容"""
    try:
        from wework_bot import bot
        
        # 生成每日消息内容但不发送
        message_content = bot.generate_daily_message()
        
        return jsonify({
            'success': True,
            'data': {
                'message_content': message_content,
                'preview_mode': True
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'预览每日消息失败: {str(e)}'
        }), 500

@message_bp.route('/send-weather', methods=['POST'])
def send_weather_message():
    """发送天气消息"""
    try:
        from wework_bot import bot
        
        # 获取天气信息并发送
        weather_info = bot.get_weather_info()
        result = bot.send_message(f"🌤️ 天气播报\n\n{weather_info}")
        
        if result:
            return jsonify({
                'success': True,
                'message': '天气消息发送成功',
                'data': {
                    'weather_info': weather_info
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': '天气消息发送失败'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'发送天气消息失败: {str(e)}'
        }), 500

@message_bp.route('/send-fortune', methods=['POST'])
def send_fortune_message():
    """发送老黄历消息"""
    try:
        from wework_bot import bot
        
        # 获取老黄历信息并发送
        fortune_info = bot.get_today_fortune()
        result = bot.send_message(f"📅 今日运势\n\n{fortune_info}")
        
        if result:
            return jsonify({
                'success': True,
                'message': '老黄历消息发送成功',
                'data': {
                    'fortune_info': fortune_info
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': '老黄历消息发送失败'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'发送老黄历消息失败: {str(e)}'
        }), 500

@message_bp.route('/send-lunch', methods=['POST'])
def send_lunch_message():
    """发送午餐推荐消息"""
    try:
        from wework_bot import bot
        
        # 获取午餐推荐并发送
        lunch_recommendation = bot.get_lunch_recommendation()
        result = bot.send_message(f"🍽️ 午餐推荐\n\n{lunch_recommendation}")
        
        if result:
            return jsonify({
                'success': True,
                'message': '午餐推荐消息发送成功',
                'data': {
                    'lunch_recommendation': lunch_recommendation
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': '午餐推荐消息发送失败'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'发送午餐推荐消息失败: {str(e)}'
        }), 500

@message_bp.route('/templates', methods=['GET'])
def get_message_templates():
    """获取消息模板列表"""
    templates = {
        'daily': {
            'name': '每日消息',
            'description': '包含天气、运势、搞笑内容和午餐推荐的完整每日消息',
            'endpoint': '/api/message/send-daily'
        },
        'weather': {
            'name': '天气播报',
            'description': '仅发送天气信息',
            'endpoint': '/api/message/send-weather'
        },
        'fortune': {
            'name': '今日运势',
            'description': '仅发送老黄历信息',
            'endpoint': '/api/message/send-fortune'
        },
        'lunch': {
            'name': '午餐推荐',
            'description': '仅发送午餐推荐',
            'endpoint': '/api/message/send-lunch'
        },
        'custom': {
            'name': '自定义消息',
            'description': '发送自定义文本消息',
            'endpoint': '/api/message/send',
            'method': 'POST',
            'body': {'message': '自定义消息内容'}
        }
    }
    
    return jsonify({
        'success': True,
        'data': {
            'templates': templates,
            'total': len(templates)
        }
    })