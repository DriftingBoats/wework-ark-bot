#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
天气API模块
"""

from flask import Blueprint, jsonify, request
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

weather_bp = Blueprint('weather', __name__, url_prefix='/weather')

@weather_bp.route('/', methods=['GET'])
def get_weather():
    """获取天气信息"""
    try:
        from wework_bot import bot
        
        # 获取查询参数
        city = request.args.get('city')
        if city:
            # 临时设置城市
            original_city = bot.city
            bot.city = city
            weather_info = bot.get_weather_info()
            bot.city = original_city
        else:
            weather_info = bot.get_weather_info()
        
        return jsonify({
            'success': True,
            'data': {
                'weather': weather_info,
                'city': city or bot.city
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取天气信息失败: {str(e)}'
        }), 500

@weather_bp.route('/current', methods=['GET'])
def get_current_weather():
    """获取当前天气（实况）"""
    try:
        from wework_bot import bot
        
        city = request.args.get('city', bot.city)
        
        # 如果有高德API密钥，获取详细天气信息
        if bot.weather_api_key:
            current_weather = bot.get_amap_current_weather()
            if current_weather:
                return jsonify({
                    'success': True,
                    'data': {
                        'current_weather': current_weather,
                        'city': city,
                        'source': 'amap_api'
                    }
                })
        
        # 降级到基础天气信息
        weather_info = bot.get_weather_info()
        return jsonify({
            'success': True,
            'data': {
                'weather': weather_info,
                'city': city,
                'source': 'fallback'
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取当前天气失败: {str(e)}'
        }), 500

@weather_bp.route('/forecast', methods=['GET'])
def get_weather_forecast():
    """获取天气预报"""
    try:
        from wework_bot import bot
        
        city = request.args.get('city', bot.city)
        
        # 如果有高德API密钥，获取预报信息
        if bot.weather_api_key:
            forecast_weather = bot.get_amap_forecast_weather()
            if forecast_weather:
                return jsonify({
                    'success': True,
                    'data': {
                        'forecast': forecast_weather,
                        'city': city,
                        'source': 'amap_api'
                    }
                })
        
        return jsonify({
            'success': False,
            'error': '天气预报功能需要配置高德API密钥'
        }), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取天气预报失败: {str(e)}'
        }), 500