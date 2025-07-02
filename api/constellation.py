#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
星座运势API模块
"""

from flask import Blueprint, jsonify, request
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

constellation_bp = Blueprint('constellation', __name__, url_prefix='/constellation')

# 星座列表
CONSTELLATIONS = [
    '白羊座', '金牛座', '双子座', '巨蟹座', '狮子座', '处女座',
    '天秤座', '天蝎座', '射手座', '摩羯座', '水瓶座', '双鱼座'
]

# 英文到中文星座名称映射
CONSTELLATION_MAP = {
    'aries': '白羊座',
    'taurus': '金牛座', 
    'gemini': '双子座',
    'cancer': '巨蟹座',
    'leo': '狮子座',
    'virgo': '处女座',
    'libra': '天秤座',
    'scorpio': '天蝎座',
    'sagittarius': '射手座',
    'capricorn': '摩羯座',
    'aquarius': '水瓶座',
    'pisces': '双鱼座'
}

def normalize_constellation_name(sign):
    """标准化星座名称，支持中英文"""
    if not sign:
        return None
    
    # 如果是中文名称，直接返回
    if sign in CONSTELLATIONS:
        return sign
    
    # 如果是英文名称，转换为中文
    sign_lower = sign.lower()
    if sign_lower in CONSTELLATION_MAP:
        return CONSTELLATION_MAP[sign_lower]
    
    return None

@constellation_bp.route('/', methods=['GET'])
def get_constellation():
    """获取星座运势"""
    try:
        from wework_bot import bot
        
        sign = request.args.get('sign')
        if not sign:
            return jsonify({
                'success': False,
                'error': '请提供星座参数',
                'available_signs': CONSTELLATIONS,
                'supported_english': list(CONSTELLATION_MAP.keys())
            }), 400
        
        # 标准化星座名称（支持中英文）
        normalized_sign = normalize_constellation_name(sign)
        if not normalized_sign:
            return jsonify({
                'success': False,
                'error': f'不支持的星座: {sign}',
                'available_signs': CONSTELLATIONS,
                'supported_english': list(CONSTELLATION_MAP.keys())
            }), 400
        
        constellation_data = bot.get_constellation_fortune_structured(normalized_sign)
        return jsonify({
            'success': True,
            'data': constellation_data,
            'sign': normalized_sign,
            'original_input': sign
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取星座运势失败: {str(e)}'
        }), 500

@constellation_bp.route('/list', methods=['GET'])
def get_constellation_list():
    """获取支持的星座列表"""
    return jsonify({
        'success': True,
        'data': {
            'constellations': CONSTELLATIONS,
            'total': len(CONSTELLATIONS)
        }
    })

@constellation_bp.route('/today', methods=['GET'])
def get_today_constellation():
    """获取今日星座运势（需要指定星座）"""
    try:
        from wework_bot import bot
        
        sign = request.args.get('sign')
        if not sign:
            return jsonify({
                'success': False,
                'error': '请提供星座参数',
                'example': '/api/constellation/today?sign=白羊座',
                'available_signs': CONSTELLATIONS,
                'supported_english': list(CONSTELLATION_MAP.keys())
            }), 400
        
        # 标准化星座名称（支持中英文）
        normalized_sign = normalize_constellation_name(sign)
        if not normalized_sign:
            return jsonify({
                'success': False,
                'error': f'不支持的星座: {sign}',
                'available_signs': CONSTELLATIONS,
                'supported_english': list(CONSTELLATION_MAP.keys())
            }), 400
        
        constellation_data = bot.get_constellation_fortune_structured(normalized_sign)
        
        # 提取今日运势重点信息
        today_info = {
            'sign': normalized_sign,
            'overall_fortune': constellation_data.get('overall_fortune', ''),
            'love_fortune': constellation_data.get('love_fortune', ''),
            'career_fortune': constellation_data.get('career_fortune', ''),
            'wealth_fortune': constellation_data.get('wealth_fortune', ''),
            'health_fortune': constellation_data.get('health_fortune', ''),
            'lucky_color': constellation_data.get('lucky_color', ''),
            'lucky_number': constellation_data.get('lucky_number', ''),
            'date': constellation_data.get('date', '')
        }
        
        return jsonify({
            'success': True,
            'data': today_info
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取今日星座运势失败: {str(e)}'
        }), 500

@constellation_bp.route('/batch', methods=['POST'])
def get_batch_constellation():
    """批量获取多个星座运势"""
    try:
        from wework_bot import bot
        
        data = request.get_json()
        if not data or 'signs' not in data:
            return jsonify({
                'success': False,
                'error': '请提供星座列表',
                'example': {'signs': ['白羊座', '金牛座']}
            }), 400
        
        signs = data['signs']
        if not isinstance(signs, list):
            return jsonify({
                'success': False,
                'error': '星座列表必须是数组格式'
            }), 400
        
        # 验证星座名称
        invalid_signs = [sign for sign in signs if sign not in CONSTELLATIONS]
        if invalid_signs:
            return jsonify({
                'success': False,
                'error': f'不支持的星座: {invalid_signs}',
                'available_signs': CONSTELLATIONS
            }), 400
        
        # 批量获取星座运势
        results = {}
        errors = {}
        
        for sign in signs:
            try:
                constellation_data = bot.get_constellation_fortune_structured(sign)
                results[sign] = constellation_data
            except Exception as e:
                errors[sign] = str(e)
        
        response_data = {
            'success': True,
            'data': results
        }
        
        if errors:
            response_data['errors'] = errors
            response_data['partial_success'] = True
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'批量获取星座运势失败: {str(e)}'
        }), 500