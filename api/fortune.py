#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
老黄历API模块
"""

from flask import Blueprint, jsonify, request
import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

fortune_bp = Blueprint('fortune', __name__, url_prefix='/fortune')

@fortune_bp.route('/', methods=['GET'])
def get_fortune():
    """获取老黄历信息"""
    try:
        from wework_bot import bot
        
        # 获取查询参数
        date_str = request.args.get('date')
        format_type = request.args.get('format', 'structured')  # structured 或 text
        
        if format_type == 'structured':
            fortune_data = bot.get_today_fortune_structured()
            return jsonify({
                'success': True,
                'data': fortune_data,
                'format': 'structured'
            })
        else:
            fortune_text = bot.get_today_fortune()
            return jsonify({
                'success': True,
                'data': {
                    'fortune_text': fortune_text
                },
                'format': 'text'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取老黄历失败: {str(e)}'
        }), 500

@fortune_bp.route('/today', methods=['GET'])
def get_today_fortune():
    """获取今日老黄历"""
    try:
        from wework_bot import bot
        
        fortune_data = bot.get_today_fortune_structured()
        return jsonify({
            'success': True,
            'data': fortune_data,
            'date': datetime.now().strftime('%Y-%m-%d')
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取今日老黄历失败: {str(e)}'
        }), 500

@fortune_bp.route('/almanac', methods=['GET'])
def get_almanac_info():
    """获取详细的黄历信息（包含宜忌、冲煞等）"""
    try:
        from wework_bot import bot
        
        # 获取结构化的老黄历数据
        fortune_data = bot.get_today_fortune_structured()
        
        # 提取详细信息
        almanac_info = {
            'date_info': fortune_data.get('date_info', {}),
            'fortune_info': fortune_data.get('fortune_info', {}),
            'wuxing_info': fortune_data.get('wuxing_info', {}),
            'festival_info': fortune_data.get('festival_info', {})
        }
        
        return jsonify({
            'success': True,
            'data': almanac_info,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取黄历详细信息失败: {str(e)}'
        }), 500

@fortune_bp.route('/simple', methods=['GET'])
def get_simple_fortune():
    """获取简化的老黄历信息（仅宜忌）"""
    try:
        from wework_bot import bot
        
        fortune_data = bot.get_today_fortune_structured()
        
        # 提取简化信息
        simple_info = {
            'lunar_date': fortune_data.get('date_info', {}).get('lunar_formatted', ''),
            'fitness': fortune_data.get('fortune_info', {}).get('fitness', ''),
            'taboo': fortune_data.get('fortune_info', {}).get('taboo', ''),
            'festival': fortune_data.get('festival_info', {}).get('festival', '')
        }
        
        return jsonify({
            'success': True,
            'data': simple_info,
            'date': datetime.now().strftime('%Y-%m-%d')
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取简化老黄历失败: {str(e)}'
        }), 500