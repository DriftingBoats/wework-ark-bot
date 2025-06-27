#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
企业微信机器人单元测试
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import os
import json
from datetime import datetime, timedelta

# 设置测试环境变量
os.environ['WEBHOOK_URL'] = 'https://test.webhook.url'
os.environ['WEATHER_API_KEY'] = 'test_weather_key'
os.environ['TIANAPI_KEY'] = 'test_tianapi_key'
os.environ['ARK_API_KEY'] = 'test_ark_key'
os.environ['CITY'] = '测试城市'

from wework_bot import WeWorkBot


class TestWeWorkBot(unittest.TestCase):
    """WeWorkBot 测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.bot = WeWorkBot()
    
    def test_init(self):
        """测试初始化"""
        self.assertEqual(self.bot.webhook_url, 'https://test.webhook.url')
        self.assertEqual(self.bot.weather_api_key, 'test_weather_key')
        self.assertEqual(self.bot.tianapi_key, 'test_tianapi_key')
        self.assertEqual(self.bot.city, '测试城市')
        self.assertIsInstance(self.bot.cache, dict)
    
    def test_cache_functionality(self):
        """测试缓存功能"""
        # 测试设置和获取缓存
        test_data = {'test': 'data'}
        cache_key = 'test_key'
        
        self.bot._set_cache(cache_key, test_data, 'weather')
        cached_data = self.bot._get_cache(cache_key)
        
        self.assertEqual(cached_data, test_data)
        
        # 测试缓存过期
        # 模拟过期的缓存
        old_time = datetime.now() - timedelta(hours=2)
        self.bot.cache[cache_key]['timestamp'] = old_time
        
        expired_data = self.bot._get_cache(cache_key)
        self.assertIsNone(expired_data)
    
    def test_sanitize_message(self):
        """测试消息清理功能"""
        # 测试敏感信息过滤
        sensitive_msg = "这是一个包含 api_key=secret123 的消息"
        sanitized = self.bot._sanitize_message(sensitive_msg)
        self.assertNotIn('secret123', sanitized)
        self.assertIn('[REDACTED]', sanitized)
        
        # 测试长度限制
        long_msg = "a" * 5000
        sanitized_long = self.bot._sanitize_message(long_msg)
        self.assertLess(len(sanitized_long), 4000)
        self.assertIn('[截断]', sanitized_long)
    
    @patch('requests.get')
    def test_get_weather_with_cache(self, mock_get):
        """测试带缓存的天气获取"""
        # 模拟API响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'status': '1',
            'forecasts': [{
                'city': '测试城市',
                'casts': [{
                    'date': '2024-01-01',
                    'dayweather': '晴',
                    'nightweather': '晴',
                    'daytemp': '25',
                    'nighttemp': '15',
                    'daywind': '东风',
                    'daypower': '3级'
                }]
            }]
        }
        mock_get.return_value = mock_response
        
        # 第一次调用应该请求API
        weather1 = self.bot.get_weather_info()
        self.assertIn('测试城市', weather1)
        mock_get.assert_called_once()
        
        # 第二次调用应该使用缓存
        mock_get.reset_mock()
        weather2 = self.bot.get_weather_info()
        self.assertEqual(weather1, weather2)
        mock_get.assert_not_called()
    
    @patch('requests.get')
    def test_get_today_fortune_with_cache(self, mock_get):
        """测试带缓存的运势获取"""
        # 模拟API响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'code': 200,
            'result': {
                'gregoriandate': '2024-01-01',
                'lunardate': '农历十二月初一',
                'fitness': '宜出行',
                'taboo': '忌动土',
                'chongsha': '冲鼠',
                'pengzu': '甲不开仓'
            }
        }
        mock_get.return_value = mock_response
        
        # 第一次调用应该请求API
        fortune1 = self.bot.get_today_fortune()
        self.assertIn('今日老黄历', fortune1)
        mock_get.assert_called_once()
        
        # 第二次调用应该使用缓存
        mock_get.reset_mock()
        fortune2 = self.bot.get_today_fortune()
        self.assertEqual(fortune1, fortune2)
        mock_get.assert_not_called()
    
    @patch('requests.post')
    def test_send_message(self, mock_post):
        """测试消息发送"""
        # 模拟成功响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'errcode': 0}
        mock_post.return_value = mock_response
        
        result = self.bot.send_message("测试消息")
        self.assertTrue(result)
        mock_post.assert_called_once()
    
    def test_retry_mechanism(self):
        """测试重试机制"""
        # 模拟一个会失败的函数
        mock_func = Mock(side_effect=[Exception("网络错误"), Exception("网络错误"), "成功"])
        
        # 测试重试成功
        result = self.bot._retry_request(mock_func)
        self.assertEqual(result, "成功")
        self.assertEqual(mock_func.call_count, 3)
    
    def test_fallback_methods(self):
        """测试备用方法"""
        # 测试备用天气
        fallback_weather = self.bot._get_fallback_weather()
        self.assertIsInstance(fallback_weather, dict)
        self.assertIn('city', fallback_weather)
        
        # 测试备用运势
        fallback_fortune = self.bot._get_fallback_fortune()
        self.assertIsInstance(fallback_fortune, str)
        self.assertIn('今日运势', fallback_fortune)
    
    def test_generate_daily_message(self):
        """测试日报生成"""
        with patch.object(self.bot, 'get_weather_info', return_value="晴天"), \
             patch.object(self.bot, 'get_today_fortune', return_value="运势不错"), \
             patch.object(self.bot, 'get_funny_bankruptcy_message', return_value="搞笑消息"), \
             patch.object(self.bot, 'get_lunch_recommendation', return_value="午餐推荐"):
            
            message = self.bot.generate_daily_message()
            self.assertIsInstance(message, str)
            self.assertIn('晴天', message)
            self.assertIn('运势不错', message)
            self.assertIn('搞笑消息', message)
            self.assertIn('午餐推荐', message)


class TestEnvironmentVariables(unittest.TestCase):
    """测试环境变量配置"""
    
    def test_missing_webhook_url(self):
        """测试缺少WEBHOOK_URL的情况"""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                WeWorkBot()
    
    def test_optional_configs(self):
        """测试可选配置"""
        with patch.dict(os.environ, {'WEBHOOK_URL': 'https://test.url'}, clear=True):
            bot = WeWorkBot()
            self.assertIsNone(bot.weather_api_key)
            self.assertIsNone(bot.tianapi_key)
            self.assertEqual(bot.city, '上海')  # 默认值


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)