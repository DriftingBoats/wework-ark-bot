#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
企业微信群机器人 - 备份版本
支持自动回复和API调用
"""

import os
import json
import hashlib
import hmac
import base64
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import logging

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class WeWorkBot:
    def __init__(self):
        self.webhook_url = os.getenv('WEBHOOK_URL')
        self.ark_api_key = os.getenv('ARK_API_KEY')
        self.ark_base_url = os.getenv('ARK_BASE_URL', 'https://ark.cn-beijing.volces.com/api/v3')
        
        if not self.webhook_url:
            logger.warning("WEBHOOK_URL 未配置")
        if not self.ark_api_key:
            logger.warning("ARK API Key 未配置，将使用本地辩论逻辑")
    
    def call_ark_api(self, message):
        """调用 Volces Engine ARK API"""
        if not self.ark_api_key or not self.ark_base_url:
            return None
            
        try:
            headers = {
                'Authorization': f'Bearer {self.ark_api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'deepseek-v3-250324',
                'messages': [
                    {
                        'role': 'system',
                        'content': '你是一个智能助手，请用简洁明了的方式回答问题。'
                    },
                    {
                        'role': 'user',
                        'content': message
                    }
                ]
            }
            
            response = requests.post(
                f'{self.ark_base_url}/chat/completions',
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    return result['choices'][0]['message']['content']
            else:
                logger.error(f"ARK API 调用失败: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"ARK API 调用异常: {str(e)}")
            
        return None
    
    def generate_reply(self, message):
        """生成回复内容"""
        # 优先使用 ARK API
        ark_reply = self.call_ark_api(message)
        if ark_reply:
            return ark_reply
        
        # 如果 ARK API 不可用，使用本地辩论逻辑
        logger.info("使用本地辩论逻辑生成回复")
        
        # 简单的关键词匹配和回复逻辑
        message_lower = message.lower()
        
        if any(keyword in message_lower for keyword in ['你好', 'hello', 'hi']):
            return "你好！我是企业微信群机器人，有什么可以帮助你的吗？"
        elif any(keyword in message_lower for keyword in ['帮助', 'help']):
            return "我可以回答问题、提供信息。直接向我提问即可！"
        elif any(keyword in message_lower for keyword in ['时间', 'time']):
            from datetime import datetime
            return f"当前时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        elif any(keyword in message_lower for keyword in ['天气', 'weather']):
            return "抱歉，我暂时无法获取天气信息。请查看天气应用或网站。"
        else:
            # 通用辩论回复
            debate_responses = [
                "这是一个很有趣的观点，不过我认为还有其他角度值得考虑。",
                "你提出的问题很好，让我们从不同的角度来分析一下。",
                "这个话题确实值得深入讨论，每个人的看法可能都不同。",
                "我理解你的观点，同时也想分享一些不同的思考。",
                "这是一个复杂的问题，可能需要综合多方面的因素来考虑。"
            ]
            import random
            return random.choice(debate_responses)
    
    def send_message(self, content):
        """发送消息到企业微信群"""
        if not self.webhook_url:
            logger.error("Webhook URL 未配置")
            return False
            
        try:
            data = {
                "msgtype": "text",
                "text": {
                    "content": content
                }
            }
            
            response = requests.post(self.webhook_url, json=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('errcode') == 0:
                    logger.info("消息发送成功")
                    return True
                else:
                    logger.error(f"消息发送失败: {result}")
            else:
                logger.error(f"HTTP请求失败: {response.status_code}")
                
        except Exception as e:
            logger.error(f"发送消息异常: {str(e)}")
            
        return False

# 创建机器人实例
bot = WeWorkBot()

@app.route('/', methods=['GET'])
def index():
    """健康检查接口"""
    return jsonify({
        'status': 'ok',
        'message': '企业微信群机器人运行中',
        'webhook_configured': bool(bot.webhook_url),
        'ark_api_configured': bool(bot.ark_api_key)
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    """接收企业微信群消息的webhook"""
    try:
        data = request.get_json()
        logger.info(f"收到webhook数据: {data}")
        
        # 这里需要根据企业微信的实际消息格式来解析
        # 以下是示例代码，需要根据实际情况调整
        if data and 'text' in data:
            message_content = data['text'].get('content', '')
            if message_content:
                # 生成回复
                reply = bot.generate_reply(message_content)
                
                # 发送回复
                if reply:
                    bot.send_message(reply)
                    
                return jsonify({'status': 'success', 'reply': reply})
        
        return jsonify({'status': 'no_action'})
        
    except Exception as e:
        logger.error(f"处理webhook异常: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/send', methods=['POST'])
def send_message():
    """手动发送消息接口"""
    try:
        data = request.get_json()
        content = data.get('content', '')
        
        if not content:
            return jsonify({'status': 'error', 'message': '消息内容不能为空'}), 400
        
        success = bot.send_message(content)
        
        if success:
            return jsonify({'status': 'success', 'message': '消息发送成功'})
        else:
            return jsonify({'status': 'error', 'message': '消息发送失败'}), 500
            
    except Exception as e:
        logger.error(f"发送消息异常: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)