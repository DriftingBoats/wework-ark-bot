#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
企业微信群机器人
提供天气、幽默话语和午餐推荐等功能
"""

import os
import os
import json
import random
import time
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from dotenv import load_dotenv
import requests
import pytz
import logging

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 配置Flask应用，避免斜杠重定向问题
app.url_map.strict_slashes = False

class WeWorkBot:
    def __init__(self):
        self.webhook_url = os.getenv('WEBHOOK_URL')
        self.weather_api_key = os.getenv('WEATHER_API_KEY')  # 可选的天气API密钥
        self.city = os.getenv('CITY', '上海')  # 默认城市
        self.ark_api_key = os.getenv('ARK_API_KEY')
        self.ark_base_url = os.getenv('ARK_BASE_URL', 'https://ark.cn-beijing.volces.com/api/v3')
        self.ark_model = os.getenv('ARK_MODEL', 'deepseek-v3-250324')
        
        # 重试配置
        self.max_retries = 3
        self.retry_delay = 1  # 秒
        
        # 缓存配置
        self.cache = {}
        self.cache_duration = {
            'weather': timedelta(hours=1),  # 天气缓存1小时
            'fortune': timedelta(hours=12)  # 老黄历缓存12小时
        }
        
        if not self.webhook_url:
            logger.warning("WEBHOOK_URL 未配置")
        if not self.ark_api_key:
            logger.warning("ARK API Key 未配置，将使用固定文案")
    
    def _is_cache_valid(self, cache_key):
        """检查缓存是否有效"""
        if cache_key not in self.cache:
            return False
        
        cache_data = self.cache[cache_key]
        cache_time = cache_data.get('timestamp')
        cache_type = cache_data.get('type')
        
        if not cache_time or cache_type not in self.cache_duration:
            return False
        
        return datetime.now() - cache_time < self.cache_duration[cache_type]
    
    def _set_cache(self, cache_key, data, cache_type):
        """设置缓存"""
        self.cache[cache_key] = {
            'data': data,
            'timestamp': datetime.now(),
            'type': cache_type
        }
    
    def _get_cache(self, cache_key):
        """获取缓存数据"""
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]['data']
        return None
    
    def _retry_request(self, func, *args, **kwargs):
        """带重试机制的请求方法"""
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    logger.warning(f"请求失败，第{attempt + 1}次重试: {e}")
                    time.sleep(self.retry_delay * (attempt + 1))  # 指数退避
                else:
                    logger.error(f"请求失败，已达到最大重试次数: {e}")
            except Exception as e:
                # 对于非网络错误，不进行重试
                raise e
        
        # 如果所有重试都失败，抛出最后一个异常
        raise last_exception
    
    def call_ark_api(self, prompt, max_tokens=200, temperature=0.9, top_p=0.95):
        """调用 Volces Engine ARK API"""
        if not self.ark_api_key or not self.ark_base_url:
            return None
            
        try:
            headers = {
                'Authorization': f'Bearer {self.ark_api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': self.ark_model,
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'max_tokens': max_tokens,
                'temperature': temperature,
                'top_p': top_p
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
                    return result['choices'][0]['message']['content'].strip()
            else:
                logger.error(f"ARK API 调用失败: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"ARK API 调用异常: {str(e)}")
            
        return None
    
    def get_weather_info(self):
        """获取天气信息（带缓存）"""
        cache_key = f"weather_{self.city}"
        
        # 检查缓存
        cached_weather = self._get_cache(cache_key)
        if cached_weather:
            logger.info("使用缓存的天气数据")
            return cached_weather
        
        try:
            # 优先使用高德天气API
            if self.weather_api_key:
                weather_data = self.get_amap_weather()
                if weather_data:
                    # 缓存天气数据
                    self._set_cache(cache_key, weather_data, 'weather')
                    return weather_data
            
            # 降级到模拟数据
            weather_conditions = [
                {'condition': '晴天', 'temp': '25°C', 'desc': '阳光明媚'},
                {'condition': '多云', 'temp': '22°C', 'desc': '云朵飘飘'},
                {'condition': '小雨', 'temp': '18°C', 'desc': '细雨绵绵'},
                {'condition': '阴天', 'temp': '20°C', 'desc': '阴云密布'},
                {'condition': '大风', 'temp': '15°C', 'desc': '风起云涌'}
            ]
            
            weather = random.choice(weather_conditions)
            weather_data = f"今日{self.city}天气：{weather['condition']} {weather['temp']}，{weather['desc']}"
            
            # 缓存模拟数据
            self._set_cache(cache_key, weather_data, 'weather')
            return weather_data
            
        except Exception as e:
            logger.error(f"获取天气信息失败: {str(e)}")
            fallback_data = "今日天气：阳光明媚，适合上班摸鱼 ☀️"
            self._set_cache(cache_key, fallback_data, 'weather')
            return fallback_data
    
    def get_amap_weather(self):
        """使用高德API获取天气信息（包含当前温度、最高最低温度）"""
        try:
            # 先获取实况天气（当前温度）
            current_weather = self.get_amap_current_weather()
            
            # 再获取预报天气（最高最低温度）
            forecast_weather = self.get_amap_forecast_weather()
            
            if current_weather and forecast_weather:
                return f"{current_weather}，{forecast_weather}"
            elif current_weather:
                return current_weather
            elif forecast_weather:
                return forecast_weather
            else:
                return None
                
        except Exception as e:
            logger.error(f"获取高德天气数据失败: {str(e)}")
            return None
    
    def get_amap_current_weather(self):
        """获取高德实况天气"""
        try:
            url = "https://restapi.amap.com/v3/weather/weatherInfo"
            params = {
                'key': self.weather_api_key,
                'city': self.city,
                'extensions': 'base'  # 实况天气
            }
            
            response = self._retry_request(requests.get, url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == '1' and data.get('lives'):
                live_data = data['lives'][0]
                city_name = live_data.get('city', self.city)
                weather = live_data.get('weather', '未知')
                temperature = live_data.get('temperature', '未知')
                winddirection = live_data.get('winddirection', '')
                windpower = live_data.get('windpower', '')
                humidity = live_data.get('humidity', '')
                
                # 获取当前星期
                from datetime import datetime
                import pytz
                now = datetime.now(pytz.timezone('Asia/Shanghai'))
                weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
                current_weekday = weekdays[now.weekday()]
                
                # 格式化天气信息
                weather_info = f"今日{city_name}天气：{weather} {temperature}°C"
                
                # 添加风力和湿度信息
                details = []
                if winddirection and windpower:
                    details.append(f"{winddirection}风{windpower}级")
                if humidity:
                    details.append(f"湿度{humidity}%")
                
                if details:
                    weather_info += f"，{' '.join(details)}"
                
                return weather_info
            else:
                logger.warning(f"高德天气API返回错误: {data.get('info', '未知错误')}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"高德天气API请求失败: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"解析高德天气数据失败: {str(e)}")
            return None
    
    def get_amap_forecast_weather(self):
        """获取高德预报天气（最高最低温度）"""
        try:
            url = "https://restapi.amap.com/v3/weather/weatherInfo"
            params = {
                'key': self.weather_api_key,
                'city': self.city,
                'extensions': 'all'  # 预报天气
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == '1' and data.get('forecasts'):
                forecast_data = data['forecasts'][0]
                if forecast_data.get('casts') and len(forecast_data['casts']) > 0:
                    today_cast = forecast_data['casts'][0]  # 今天的预报
                    
                    daytemp = today_cast.get('daytemp', '未知')
                    nighttemp = today_cast.get('nighttemp', '未知')
                    dayweather = today_cast.get('dayweather', '未知')
                    nightweather = today_cast.get('nightweather', '未知')
                    
                    # 格式化预报信息
                    if daytemp != '未知' and nighttemp != '未知':
                        temp_range = f"最高{daytemp}°C/最低{nighttemp}°C"
                        
                        # 如果白天和晚上天气不同，显示详细信息
                        if dayweather != nightweather and dayweather != '未知' and nightweather != '未知':
                            temp_range += f"（白天{dayweather}/夜间{nightweather}）"
                        
                        return temp_range
                        
            logger.warning(f"高德预报天气API返回错误: {data.get('info', '未知错误')}")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"高德预报天气API请求失败: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"解析高德预报天气数据失败: {str(e)}")
            return None
    
    def get_today_fortune_structured(self):
        """获取今日运势（老黄历）结构化数据"""
        today = datetime.now().strftime('%Y-%m-%d')
        cache_key = f"fortune_structured_{today}"
        
        # 检查缓存
        cached_fortune = self._get_cache(cache_key)
        if cached_fortune:
            logger.info("使用缓存的结构化运势数据")
            return cached_fortune
        
        try:
            # 天行数据老黄历API
            api_url = "https://apis.tianapi.com/lunar/index"
            tianapi_key = os.getenv('TIANAPI_KEY')
            
            # 必须有API密钥才能调用
            if not tianapi_key:
                logger.warning("TIANAPI_KEY未配置，使用备用运势")
                fortune_data = self._get_fallback_fortune_structured()
                self._set_cache(cache_key, fortune_data, 'fortune')
                return fortune_data
            
            params = {'key': tianapi_key}
            response = self._retry_request(requests.get, api_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # 检查API返回的错误码
                if data.get('code') != 200:
                    error_msg = data.get('msg', '未知错误')
                    logger.error(f"天行API错误 (code: {data.get('code')}): {error_msg}")
                    fortune_data = self._get_fallback_fortune_structured()
                    self._set_cache(cache_key, fortune_data, 'fortune')
                    return fortune_data
                
                if 'result' not in data:
                    logger.error("天行API返回数据格式错误：缺少result字段")
                    fortune_data = self._get_fallback_fortune_structured()
                    self._set_cache(cache_key, fortune_data, 'fortune')
                    return fortune_data
                
                result = data['result']
                
                # 构建结构化数据
                fortune_data = {
                    'date_info': {
                        'gregorian_date': result.get('gregoriandate', ''),
                        'lunar_date': result.get('lunardate', ''),
                        'lunar_day': result.get('lunarday', ''),
                        'lunar_formatted': self._format_lunar_date(result.get('lunardate', ''), result.get('lunarday', '')),
                        'lunar_month_name': result.get('lmonthname', ''),
                        'year_ganzhi': result.get('tiangandizhiyear', ''),
                        'month_ganzhi': result.get('tiangandizhimonth', ''),
                        'day_ganzhi': result.get('tiangandizhiday', ''),
                        'shengxiao': result.get('shengxiao', '')
                    },
                    'festival_info': {
                        'lunar_festival': result.get('lunar_festival', ''),
                        'festival': result.get('festival', ''),
                        'jieqi': result.get('jieqi', '')
                    },
                    'fortune_info': {
                        'fitness': result.get('fitness', '无特别宜事'),
                        'taboo': result.get('taboo', '无特别忌事'),
                        'shenwei': result.get('shenwei', ''),
                        'taishen': result.get('taishen', ''),
                        'chongsha': result.get('chongsha', ''),
                        'suisha': result.get('suisha', ''),
                        'xingsu': result.get('xingsu', ''),
                        'jianshen': result.get('jianshen', ''),
                        'pengzu': result.get('pengzu', '')
                    },
                    'wuxing_info': {
                        'wuxingjiazi': result.get('wuxingjiazi', ''),
                        'wuxingnayear': result.get('wuxingnayear', ''),
                        'wuxingnamonth': result.get('wuxingnamonth', '')
                    }
                }
                
                logger.info("成功获取今日结构化运势信息")
                
                # 缓存运势数据
                self._set_cache(cache_key, fortune_data, 'fortune')
                return fortune_data
                
            else:
                logger.error(f"老黄历API请求失败: HTTP {response.status_code}")
                fortune_data = self._get_fallback_fortune_structured()
                self._set_cache(cache_key, fortune_data, 'fortune')
                return fortune_data
                
        except requests.exceptions.Timeout:
            logger.error("老黄历API请求超时")
            fortune_data = self._get_fallback_fortune_structured()
            self._set_cache(cache_key, fortune_data, 'fortune')
            return fortune_data
        except requests.exceptions.RequestException as e:
            logger.error(f"老黄历API网络请求失败: {str(e)}")
            fortune_data = self._get_fallback_fortune_structured()
            self._set_cache(cache_key, fortune_data, 'fortune')
            return fortune_data
        except Exception as e:
            logger.error(f"获取今日运势失败: {str(e)}")
            fortune_data = self._get_fallback_fortune_structured()
            self._set_cache(cache_key, fortune_data, 'fortune')
            return fortune_data

    def get_today_fortune(self):
        """获取今日运势（老黄历）带缓存"""
        today = datetime.now().strftime('%Y-%m-%d')
        cache_key = f"fortune_{today}"
        
        # 检查缓存
        cached_fortune = self._get_cache(cache_key)
        if cached_fortune:
            logger.info("使用缓存的运势数据")
            return cached_fortune
        
        try:
            # 天行数据老黄历API
            api_url = "https://apis.tianapi.com/lunar/index"
            tianapi_key = os.getenv('TIANAPI_KEY')
            
            # 必须有API密钥才能调用
            if not tianapi_key:
                logger.warning("TIANAPI_KEY未配置，使用备用运势")
                fortune_data = self._get_fallback_fortune()
                self._set_cache(cache_key, fortune_data, 'fortune')
                return fortune_data
            
            params = {'key': tianapi_key}
            response = self._retry_request(requests.get, api_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # 检查API返回的错误码
                if data.get('code') != 200:
                    error_msg = data.get('msg', '未知错误')
                    logger.error(f"天行API错误 (code: {data.get('code')}): {error_msg}")
                    fortune_data = self._get_fallback_fortune()
                    self._set_cache(cache_key, fortune_data, 'fortune')
                    return fortune_data
                
                if 'result' not in data:
                    logger.error("天行API返回数据格式错误：缺少result字段")
                    fortune_data = self._get_fallback_fortune()
                    self._set_cache(cache_key, fortune_data, 'fortune')
                    return fortune_data
                
                result = data['result']
                
                # 提取所有老黄历信息
                gregorian_date = result.get('gregoriandate', '')
                lunar_date = result.get('lunardate', '')
                lunar_day = result.get('lunarday', '')
                lunar_festival = result.get('lunar_festival', '')
                festival = result.get('festival', '')
                fitness = result.get('fitness', '无特别宜事')
                taboo = result.get('taboo', '无特别忌事')
                shenwei = result.get('shenwei', '')
                taishen = result.get('taishen', '')
                chongsha = result.get('chongsha', '')
                suisha = result.get('suisha', '')
                wuxingjiazi = result.get('wuxingjiazi', '')
                wuxingnayear = result.get('wuxingnayear', '')
                wuxingnamonth = result.get('wuxingnamonth', '')
                xingsu = result.get('xingsu', '')
                pengzu = result.get('pengzu', '')
                jianshen = result.get('jianshen', '')
                tiangandizhiyear = result.get('tiangandizhiyear', '')
                tiangandizhimonth = result.get('tiangandizhimonth', '')
                tiangandizhiday = result.get('tiangandizhiday', '')
                lmonthname = result.get('lmonthname', '')
                shengxiao = result.get('shengxiao', '')
                lubarmonth = result.get('lubarmonth', '')
                jieqi = result.get('jieqi', '')
                
                # 格式化运势信息（只显示农历日期和宜忌）
                fortune_lines = []
                
                # 处理农历日期格式，转换为传统格式
                if lunar_date and lunar_day:
                    # 将YYYY-MM-DD格式转换为传统农历格式
                    lunar_formatted = self._format_lunar_date(lunar_date, lunar_day)
                    fortune_lines.append(f"🌝 农历：{lunar_formatted}")
                else:
                    fortune_lines.append("🌝 农历：信息获取中...")
                
                fortune_lines.append(f"✅ 宜：{fitness}")
                fortune_lines.append(f"❌ 忌：{taboo}")
                
                # 简化冲煞信息，用大白话表述
                if chongsha:
                    simplified_chongsha = self._simplify_chongsha(chongsha)
                    if simplified_chongsha:
                        fortune_lines.append(f"⚡ 今日提醒：{simplified_chongsha}")
                
                # 彭祖百忌太晦涩，直接省略不显示
                
                fortune_text = "\n".join(fortune_lines)
                logger.info("成功获取今日运势信息")
                
                # 缓存运势数据
                self._set_cache(cache_key, fortune_text, 'fortune')
                return fortune_text
                
            else:
                logger.error(f"老黄历API请求失败: HTTP {response.status_code}")
                fortune_data = self._get_fallback_fortune()
                self._set_cache(cache_key, fortune_data, 'fortune')
                return fortune_data
                
        except requests.exceptions.Timeout:
            logger.error("老黄历API请求超时")
            fortune_data = self._get_fallback_fortune()
            self._set_cache(cache_key, fortune_data, 'fortune')
            return fortune_data
        except requests.exceptions.RequestException as e:
            logger.error(f"老黄历API网络请求失败: {str(e)}")
            fortune_data = self._get_fallback_fortune()
            self._set_cache(cache_key, fortune_data, 'fortune')
            return fortune_data
        except Exception as e:
            logger.error(f"获取今日运势失败: {str(e)}")
            fortune_data = self._get_fallback_fortune()
            self._set_cache(cache_key, fortune_data, 'fortune')
            return fortune_data
    
    def _format_lunar_date(self, lunar_date, lunar_day):
        """格式化农历日期为传统格式"""
        try:
            # 如果lunar_date是YYYY-MM-DD格式，转换为干支年
            if '-' in lunar_date:
                year_part = lunar_date.split('-')[0]
                year_int = int(year_part)
                
                # 转换为干支年
                gan_zhi_year = self._get_ganzhi_year(year_int)
                
                # 提取月份信息
                month_part = lunar_date.split('-')[1] if len(lunar_date.split('-')) > 1 else ''
                
                # 格式化为传统农历格式
                if month_part:
                    month_int = int(month_part)
                    month_names = ['', '正月', '二月', '三月', '四月', '五月', '六月', 
                                 '七月', '八月', '九月', '十月', '冬月', '腊月']
                    month_name = month_names[month_int] if 1 <= month_int <= 12 else f'{month_int}月'
                    return f"{gan_zhi_year}年{month_name}{lunar_day}"
                else:
                    return f"{gan_zhi_year}年{lunar_day}"
            else:
                # 如果已经是传统格式，直接使用
                return f"{lunar_date} {lunar_day}"
        except:
            # 如果转换失败，返回原始格式
            return f"{lunar_date} {lunar_day}"
    
    def _get_ganzhi_year(self, year):
        """获取干支年"""
        try:
            # 天干
            tiangan = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
            # 地支
            dizhi = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
            
            # 计算干支（以1984年甲子年为基准）
            base_year = 1984
            offset = (year - base_year) % 60
            
            tian_index = offset % 10
            di_index = offset % 12
            
            return f"{tiangan[tian_index]}{dizhi[di_index]}"
        except:
            return str(year)
    
    def _simplify_chongsha(self, chongsha):
        """简化冲煞信息为大白话"""
        if not chongsha:
            return None
            
        # 提取生肖信息
        animals = ['鼠', '牛', '虎', '兔', '龙', '蛇', '马', '羊', '猴', '鸡', '狗', '猪']
        
        for animal in animals:
            if animal in chongsha:
                return f"属{animal}的朋友今天要低调一些"
        
        # 如果没有找到生肖，返回通用提醒
        return "今天做事要谨慎一些"
    
    def _get_fallback_fortune_structured(self):
        """获取备用结构化运势信息"""
        today = datetime.now().strftime('%Y-%m-%d')
        fallback_data = {
            'date_info': {
                'gregorian_date': today,
                'lunar_date': '农历信息获取中...',
                'lunar_day': '',
                'lunar_formatted': '农历信息获取中...',
                'lunar_month_name': '',
                'year_ganzhi': '',
                'month_ganzhi': '',
                'day_ganzhi': '',
                'shengxiao': ''
            },
            'festival_info': {
                'lunar_festival': '',
                'festival': '',
                'jieqi': ''
            },
            'fortune_info': {
                'fitness': random.choice(['摸鱼、划水、发呆', '午休、喝茶、聊天', '保持低调、适度摸鱼', '网上冲浪、刷手机', '装忙、假装思考']),
                'taboo': random.choice(['加班、开会、写报告', '认真工作、主动汇报', '表现积极、承担责任', '提升自己、努力奋斗', '真的很忙、真的在想']),
                'shenwei': '',
                'taishen': '',
                'chongsha': '',
                'suisha': '',
                'xingsu': '',
                'jianshen': '',
                'pengzu': ''
            },
            'wuxing_info': {
                'wuxingjiazi': '',
                'wuxingnayear': '',
                'wuxingnamonth': ''
            }
        }
        return fallback_data

    def _get_fallback_fortune(self):
        """获取备用运势信息"""
        fallback_fortunes = [
            "📅 农历信息获取中...\n✅ 宜：摸鱼、划水、发呆\n❌ 忌：加班、开会、写报告",
            "📅 今日黄历\n✅ 宜：午休、喝茶、聊天\n❌ 忌：认真工作、主动汇报",
            "📅 老黄历提醒\n✅ 宜：保持低调、适度摸鱼\n❌ 忌：表现积极、承担责任",
            "📅 运势播报\n✅ 宜：网上冲浪、刷手机\n❌ 忌：提升自己、努力奋斗",
            "📅 今日宜忌\n✅ 宜：装忙、假装思考\n❌ 忌：真的很忙、真的在想"
        ]
        return random.choice(fallback_fortunes)
    
    def get_constellation_fortune_structured(self, sign):
        """获取星座运势结构化数据（带缓存）"""
        today = datetime.now().strftime('%Y-%m-%d')
        cache_key = f"constellation_structured_{sign}_{today}"
        
        # 检查缓存
        cached_constellation = self._get_cache(cache_key)
        if cached_constellation:
            logger.info(f"使用缓存的{sign}星座结构化运势数据")
            return cached_constellation
        
        try:
            # 天行数据星座运势API
            api_url = "https://apis.tianapi.com/star/index"
            tianapi_key = os.getenv('TIANAPI_KEY')
            
            # 必须有API密钥才能调用
            if not tianapi_key:
                logger.warning("TIANAPI_KEY未配置，使用备用星座运势")
                constellation_data = self._get_fallback_constellation_structured(sign)
                self._set_cache(cache_key, constellation_data, 'fortune')
                return constellation_data
            
            # 星座名称映射
            constellation_map = {
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
            
            chinese_sign = constellation_map.get(sign, sign)
            
            params = {
                'key': tianapi_key,
                'astro': sign  # 使用英文星座名称
            }
            
            response = self._retry_request(requests.get, api_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # 检查API返回的错误码
                if data.get('code') != 200:
                    error_msg = data.get('msg', '未知错误')
                    logger.error(f"天行星座API错误 (code: {data.get('code')}): {error_msg}")
                    constellation_data = self._get_fallback_constellation_structured(sign)
                    self._set_cache(cache_key, constellation_data, 'fortune')
                    return constellation_data
                
                if 'result' not in data or 'list' not in data['result']:
                    logger.error("天行星座API返回数据格式错误：缺少result.list字段")
                    constellation_data = self._get_fallback_constellation_structured(sign)
                    self._set_cache(cache_key, constellation_data, 'fortune')
                    return constellation_data
                
                result_list = data['result']['list']
                
                # 解析星座运势信息
                constellation_info = {}
                for item in result_list:
                    item_type = item.get('type', '')
                    content = item.get('content', '')
                    
                    if item_type == '综合指数':
                        constellation_info['comprehensive'] = content
                    elif item_type == '爱情指数':
                        constellation_info['love_index'] = content
                    elif item_type == '工作指数':
                        constellation_info['work_index'] = content
                    elif item_type == '财运指数':
                        constellation_info['money_index'] = content
                    elif item_type == '健康指数':
                        constellation_info['health_index'] = content
                    elif item_type == '幸运颜色':
                        constellation_info['lucky_color'] = content
                    elif item_type == '幸运数字':
                        constellation_info['lucky_number'] = content
                    elif item_type == '贵人星座':
                        constellation_info['noble_sign'] = content
                    elif item_type == '今日概述':
                        constellation_info['summary'] = content
                    elif item_type == '幸运时间':
                        constellation_info['lucky_time'] = content
                    elif item_type == '今日建议':
                        constellation_info['advice'] = content
                
                # 构建结构化数据
                constellation_data = {
                    'sign': chinese_sign,
                    'date': today,
                    'summary': constellation_info.get('summary', ''),
                    'indices': {
                        'comprehensive': self._extract_number(constellation_info.get('comprehensive', '0')),
                        'love': self._extract_number(constellation_info.get('love_index', '0')),
                        'work': self._extract_number(constellation_info.get('work_index', '0')),
                        'money': self._extract_number(constellation_info.get('money_index', '0')),
                        'health': self._extract_number(constellation_info.get('health_index', '0'))
                    },
                    'lucky_info': {
                        'color': constellation_info.get('lucky_color', ''),
                        'number': constellation_info.get('lucky_number', ''),
                        'time': constellation_info.get('lucky_time', ''),
                        'noble_sign': constellation_info.get('noble_sign', '')
                    },
                    'advice': constellation_info.get('advice', '')
                }
                
                logger.info(f"成功获取{chinese_sign}结构化运势信息")
                
                # 缓存星座运势数据
                self._set_cache(cache_key, constellation_data, 'fortune')
                return constellation_data
                
            else:
                logger.error(f"星座运势API请求失败: HTTP {response.status_code}")
                constellation_data = self._get_fallback_constellation_structured(sign)
                self._set_cache(cache_key, constellation_data, 'fortune')
                return constellation_data
                
        except requests.exceptions.Timeout:
            logger.error("星座运势API请求超时")
            constellation_data = self._get_fallback_constellation_structured(sign)
            self._set_cache(cache_key, constellation_data, 'fortune')
            return constellation_data
        except requests.exceptions.RequestException as e:
            logger.error(f"星座运势API网络请求失败: {str(e)}")
            constellation_data = self._get_fallback_constellation_structured(sign)
            self._set_cache(cache_key, constellation_data, 'fortune')
            return constellation_data
        except Exception as e:
            logger.error(f"获取星座运势失败: {str(e)}")
            constellation_data = self._get_fallback_constellation_structured(sign)
            self._set_cache(cache_key, constellation_data, 'fortune')
            return constellation_data

    def get_constellation_fortune(self, sign):
        """获取星座运势（带缓存）"""
        today = datetime.now().strftime('%Y-%m-%d')
        cache_key = f"constellation_{sign}_{today}"
        
        # 检查缓存
        cached_constellation = self._get_cache(cache_key)
        if cached_constellation:
            logger.info(f"使用缓存的{sign}星座运势数据")
            return cached_constellation
        
        try:
            # 天行数据星座运势API
            api_url = "https://apis.tianapi.com/star/index"
            tianapi_key = os.getenv('TIANAPI_KEY')
            
            # 必须有API密钥才能调用
            if not tianapi_key:
                logger.warning("TIANAPI_KEY未配置，使用备用星座运势")
                constellation_data = self._get_fallback_constellation(sign)
                self._set_cache(cache_key, constellation_data, 'fortune')
                return constellation_data
            
            # 星座名称映射
            constellation_map = {
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
            
            chinese_sign = constellation_map.get(sign, sign)
            
            params = {
                'key': tianapi_key,
                'astro': sign  # 使用英文星座名称
            }
            
            response = self._retry_request(requests.get, api_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # 检查API返回的错误码
                if data.get('code') != 200:
                    error_msg = data.get('msg', '未知错误')
                    logger.error(f"天行星座API错误 (code: {data.get('code')}): {error_msg}")
                    constellation_data = self._get_fallback_constellation(sign)
                    self._set_cache(cache_key, constellation_data, 'fortune')
                    return constellation_data
                
                if 'result' not in data or 'list' not in data['result']:
                    logger.error("天行星座API返回数据格式错误：缺少result.list字段")
                    constellation_data = self._get_fallback_constellation(sign)
                    self._set_cache(cache_key, constellation_data, 'fortune')
                    return constellation_data
                
                result_list = data['result']['list']
                
                # 解析星座运势信息
                constellation_info = {}
                for item in result_list:
                    item_type = item.get('type', '')
                    content = item.get('content', '')
                    
                    if item_type == '综合指数':
                        constellation_info['comprehensive'] = content
                    elif item_type == '爱情指数':
                        constellation_info['love_index'] = content
                    elif item_type == '工作指数':
                        constellation_info['work_index'] = content
                    elif item_type == '财运指数':
                        constellation_info['money_index'] = content
                    elif item_type == '健康指数':
                        constellation_info['health_index'] = content
                    elif item_type == '幸运颜色':
                        constellation_info['lucky_color'] = content
                    elif item_type == '幸运数字':
                        constellation_info['lucky_number'] = content
                    elif item_type == '贵人星座':
                        constellation_info['noble_sign'] = content
                    elif item_type == '今日概述':
                        constellation_info['summary'] = content
                
                # 格式化星座运势信息
                fortune_lines = []
                fortune_lines.append(f"⭐ {chinese_sign}今日运势")
                fortune_lines.append(f"📅 日期：{today}")
                
                if constellation_info.get('summary'):
                    fortune_lines.append(f"📝 今日概述：{constellation_info['summary']}")
                
                if constellation_info.get('comprehensive'):
                    fortune_lines.append(f"🌟 综合指数：{constellation_info['comprehensive']}")
                
                if constellation_info.get('love_index'):
                    fortune_lines.append(f"💕 爱情指数：{constellation_info['love_index']}")
                
                if constellation_info.get('work_index'):
                    fortune_lines.append(f"💼 工作指数：{constellation_info['work_index']}")
                
                if constellation_info.get('money_index'):
                    fortune_lines.append(f"💰 财运指数：{constellation_info['money_index']}")
                
                if constellation_info.get('health_index'):
                    fortune_lines.append(f"🏥 健康指数：{constellation_info['health_index']}")
                
                if constellation_info.get('lucky_color'):
                    fortune_lines.append(f"🎨 幸运颜色：{constellation_info['lucky_color']}")
                
                if constellation_info.get('lucky_number'):
                    fortune_lines.append(f"🔢 幸运数字：{constellation_info['lucky_number']}")
                
                if constellation_info.get('noble_sign'):
                    fortune_lines.append(f"🤝 贵人星座：{constellation_info['noble_sign']}")
                
                constellation_text = "\n".join(fortune_lines)
                logger.info(f"成功获取{chinese_sign}运势信息")
                
                # 缓存星座运势数据
                self._set_cache(cache_key, constellation_text, 'fortune')
                return constellation_text
                
            else:
                logger.error(f"星座运势API请求失败: HTTP {response.status_code}")
                constellation_data = self._get_fallback_constellation(sign)
                self._set_cache(cache_key, constellation_data, 'fortune')
                return constellation_data
                
        except requests.exceptions.Timeout:
            logger.error("星座运势API请求超时")
            constellation_data = self._get_fallback_constellation(sign)
            self._set_cache(cache_key, constellation_data, 'fortune')
            return constellation_data
        except requests.exceptions.RequestException as e:
            logger.error(f"星座运势API网络请求失败: {str(e)}")
            constellation_data = self._get_fallback_constellation(sign)
            self._set_cache(cache_key, constellation_data, 'fortune')
            return constellation_data
        except Exception as e:
            logger.error(f"获取星座运势失败: {str(e)}")
            constellation_data = self._get_fallback_constellation(sign)
            self._set_cache(cache_key, constellation_data, 'fortune')
            return constellation_data
    
    def _extract_number(self, text):
        """从文本中提取数字"""
        import re
        if not text:
            return 0
        # 查找文本中的数字
        numbers = re.findall(r'\d+', str(text))
        if numbers:
            return int(numbers[0])
        return 0

    def _get_fallback_constellation_structured(self, sign):
        """获取备用星座运势结构化信息"""
        constellation_names = {
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
        
        chinese_name = constellation_names.get(sign, sign)
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 随机生成备用数据
        summaries = [
            '运势平稳，适合保持低调',
            '今天心情不错，做事比较顺利',
            '需要多注意细节，避免出错',
            '整体运势不错，心情愉悦'
        ]
        
        colors = ['蓝色', '红色', '绿色', '黄色', '紫色', '橙色']
        numbers = ['3', '7', '8', '5', '9', '6']
        times = ['上午9-11点', '下午2-4点', '晚上7-9点', '中午12-1点']
        noble_signs = ['天秤座', '双鱼座', '狮子座', '处女座', '金牛座']
        advices = [
            '保持积极心态，机会就在眼前',
            '多与朋友交流，会有意外收获',
            '注意休息，劳逸结合很重要',
            '相信自己的直觉，做出正确选择'
        ]
        
        fallback_data = {
            'sign': chinese_name,
            'date': today,
            'summary': random.choice(summaries),
            'indices': {
                'comprehensive': random.randint(60, 90),
                'love': random.randint(50, 95),
                'work': random.randint(55, 88),
                'money': random.randint(45, 85),
                'health': random.randint(60, 92)
            },
            'lucky_info': {
                'color': random.choice(colors),
                'number': random.choice(numbers),
                'time': random.choice(times),
                'noble_sign': random.choice(noble_signs)
            },
            'advice': random.choice(advices)
        }
        
        return fallback_data

    def _get_fallback_constellation(self, sign):
        """获取备用星座运势信息"""
        constellation_names = {
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
        
        chinese_name = constellation_names.get(sign, sign)
        
        fallback_fortunes = [
            f"⭐ {chinese_name}今日运势\n📝 今日概述：运势平稳，适合保持低调\n💕 爱情运势：桃花运一般，单身的朋友继续等待\n💼 事业运势：工作顺利，但不宜冒进\n💰 财运：财运平平，适合理财\n🎨 幸运颜色：蓝色\n🔢 幸运数字：7",
            f"⭐ {chinese_name}今日运势\n📝 今日概述：今天心情不错，做事比较顺利\n💕 爱情运势：有机会遇到心仪的人\n💼 事业运势：工作效率高，容易获得认可\n💰 财运：有小财进账的可能\n🎨 幸运颜色：红色\n🔢 幸运数字：3",
            f"⭐ {chinese_name}今日运势\n📝 今日概述：需要多注意细节，避免出错\n💕 爱情运势：感情稳定，适合深入交流\n💼 事业运势：工作中可能遇到小挑战\n💰 财运：支出较多，注意控制消费\n🎨 幸运颜色：绿色\n🔢 幸运数字：5",
            f"⭐ {chinese_name}今日运势\n📝 今日概述：整体运势不错，心情愉悦\n💕 爱情运势：适合表达情感，增进感情\n💼 事业运势：有新的机会出现\n💰 财运：投资运佳，可适当尝试\n🎨 幸运颜色：黄色\n🔢 幸运数字：8"
        ]
        
        return random.choice(fallback_fortunes)

    def get_work_encouragement(self, current_weekday):
        """根据工作日生成哄用户上班的鼓励话语"""
        # 优先使用大模型生成
        if self.ark_api_key:
            # 社畜黑色幽默风格的鼓励话语
            encouragement_styles = [
                f"请以一个资深社畜的第一人称视角，为{current_weekday}写一句带有黑色幽默的自嘲式上班鼓励语",
                f"请模仿一个已经麻木但依然坚强的打工人，为{current_weekday}生成一句苦中作乐的上班感悟",
                f"请以一个在职场摸爬滚打多年的老社畜口吻，为{current_weekday}写一句既丧又燃的工作箴言",
                f"请模仿一个对工作又爱又恨的社畜，为{current_weekday}生成一句充满矛盾情感的上班独白",
                f"请以一个习惯了996但依然保持幽默感的打工人身份，为{current_weekday}写一句自我安慰式的工作感言",
                f"请模仿一个在格子间里求生存的社畜，为{current_weekday}生成一句带有生存智慧的上班心得",
                f"请以一个经历过无数加班夜晚的老员工视角，为{current_weekday}写一句既现实又温暖的工作感悟",
                f"请模仿一个在职场浮沉中找到平衡的社畜，为{current_weekday}生成一句充满人生哲理的上班语录",
                f"请以一个对现状无奈但依然努力的打工人口吻，为{current_weekday}写一句自嘲中带着坚韧的工作宣言",
                f"请模仿一个在都市生活压力下依然保持乐观的社畜，为{current_weekday}生成一句苦涩中带甜的上班感言"
            ]
            
            style = random.choice(encouragement_styles)
            prompt = f"""{style}。
            
要求：
1. 必须使用第一人称来叙述
2. 语调要有黑色幽默感，既丧又不失希望
3. 体现社畜的真实心理状态和生存智慧
4. 长度控制在2-3句话，要有画面感
5. 可以适当自嘲，但要有积极的底色
6. 结合{current_weekday}的特殊感受（如周一的绝望、周五的期待等）
7. 语言要接地气，有共鸣感
8. 适当使用emoji，但不要过多
9. 可以提及咖啡、地铁等社畜日常元素

请直接输出鼓励话语，不要解释。"""
            
            ai_encouragement = self.call_ark_api(prompt, max_tokens=100, temperature=0.95, top_p=0.9)
            if ai_encouragement:
                return ai_encouragement
        
        # 降级到固定文案
        encouragements = {
            '周一': [
                "新的一周开始啦！虽然有点困，但是想想周末的美好，今天也要元气满满哦~ 💪",
                "周一蓝调？不存在的！今天是新开始，让我们一起创造美好的回忆吧~ ✨",
                "Monday Blues退散！今天的你一定会遇到很多美好的事情~ 🌟"
            ],
            '周二': [
                "周二是一周中最有潜力的一天！昨天的疲惫已经过去，今天充满无限可能~ 🚀",
                "Tuesday能量日！今天的效率一定会让你惊喜的，加油鸭~ 💫",
                "周二小贴士：保持微笑，好运自然来！今天也要开开心心的~ 😊"
            ],
            '周三': [
                "恭喜你！一周已经过半啦！坚持就是胜利，你已经很棒了~ 🎉",
                "Wednesday Wisdom：今天是转折点，下半周会越来越轻松的~ 🌈",
                "周三加油站！给自己一个大大的拥抱，你值得所有的美好~ 🤗"
            ],
            '周四': [
                "Thursday Power！明天就是快乐星期五啦，今天再努力一点点~ 💪",
                "周四小确幸：距离周末只有一天了！今天的每一分努力都值得~ ⭐",
                "Thursday Motivation：你已经走了这么远，最后一天也要漂亮收官~ 🏆"
            ],
            '周五': [
                "TGIF！Thank God It's Friday！周末在向你招手啦~ 🙌",
                "Friday Feeling！今天心情特别好对不对？让我们愉快地结束这一周~ 🎊",
                "周五福利：今天可以稍微摸摸鱼，毕竟马上就周末了嘛~ 🐟"
            ]
        }
        
        weekday_encouragements = encouragements.get(current_weekday, [
            "今天也要加油哦！每一天都是新的开始~ ✨"
        ])
        
        return random.choice(weekday_encouragements)
    
    def get_lunch_recommendation(self, weather_info):
        """根据天气推荐午餐"""
        # 优先使用大模型生成
        if self.ark_api_key:
            # 外卖达人推荐风格
            recommendation_styles = [
                f"请以资深外卖达人的丰富经验，根据天气'{weather_info}'推荐一款适合的外卖",
                f"请模仿外卖评测专家的专业眼光，结合天气'{weather_info}'推荐一份性价比超高的外卖",
                f"请以外卖老司机的身份，根据天气'{weather_info}'推荐一款口碑爆棚的外卖",
                f"请模仿美食博主的推荐风格，结合天气'{weather_info}'推荐一份网红外卖",
                f"请以外卖平台金牌用户的角度，根据天气'{weather_info}'推荐一款必点外卖",
                f"请模仿外卖探店达人的口吻，结合天气'{weather_info}'推荐一份隐藏好店的外卖",
                f"请以外卖重度用户的经验，根据天气'{weather_info}'推荐一款治愈系外卖",
                f"请模仿外卖种草机的风格，结合天气'{weather_info}'推荐一份让人欲罢不能的外卖",
                f"请以外卖品鉴师的专业态度，根据天气'{weather_info}'推荐一款品质上乘的外卖",
                f"请模仿外卖攻略达人的推荐方式，结合天气'{weather_info}'推荐一份超值外卖套餐",
                f"请以外卖美食家的品味，根据天气'{weather_info}'推荐一款精选外卖",
                f"请模仿外卖测评师的客观视角，结合天气'{weather_info}'推荐一份值得回购的外卖"
            ]
            
            style = random.choice(recommendation_styles)
            prompt = f"""{style}。
            
要求：
1. 语言要接地气，像真正的外卖达人在分享经验
2. 推荐具体的外卖店铺类型或菜品类别
3. 解释为什么这个外卖选择适合当前天气
4. 可以提及配送时间、性价比、口味特点等实用信息
5. 体现对外卖平台和商家的了解
6. 包含一些外卖小贴士或避坑指南
7. 长度控制在2-3句话，要实用有趣
8. 语调要亲切自然，像朋友推荐
9. 可以提及外卖平台活动、优惠券等实用信息
10. 使用网络流行语，但要适度
11. 要有外卖老用户的实战经验感
12. 适当使用emoji，营造轻松氛围

请直接输出推荐内容，不要解释。"""
            
            ai_recommendation = self.call_ark_api(prompt, max_tokens=150, temperature=0.95, top_p=0.9)
            if ai_recommendation:
                return ai_recommendation
        
        # 降级到固定外卖推荐文案
        if '晴' in weather_info or '阳光' in weather_info:
            recommendations = [
                "晴天外卖推荐：轻食沙拉、日式便当，记得点杯冰饮 🍱❄️",
                "阳光明媚适合点烤肉外卖，配个气泡水超爽！ 🍖🥤",
                "好天气点个网红寿司外卖，颜值味道都在线 🍣✨"
            ]
        elif '雨' in weather_info:
            recommendations = [
                "下雨天外卖首选：麻辣烫、小火锅，暖胃又暖心 🍜☔",
                "雨天点个粥店外卖，热腾腾的很治愈 🍲💕",
                "下雨天就要川菜外卖，辣到出汗忘记阴冷 🌶️🔥"
            ]
        elif '阴' in weather_info or '云' in weather_info:
            recommendations = [
                "阴天外卖推荐：中式快餐，红烧肉盖饭yyds 🥘",
                "多云天气点个炒饭外卖，简单满足 🍚😋",
                "阴天来份温和系外卖：蒸蛋羹、小馄饨很舒服 🥟💛"
            ]
        elif '风' in weather_info:
            recommendations = [
                "大风天外卖要选饱腹系：汉堡、炸鸡，管饱管爽 🍔💪",
                "风大点个包子店外卖，热乎乎的最暖胃 🥟🌪️",
                "刮风天来份重口味外卖：麻辣香锅、水煮鱼片 🐟🌶️"
            ]
        else:
            recommendations = [
                "今天外卖盲盒：闭眼点个评分高的，惊喜等你 🍱🎲",
                "不知道点啥外卖？看看昨天收藏夹里的店 🤷📱",
                "外卖推荐：跟着热销榜走，踩雷概率小 📈✨"
            ]
        
        return random.choice(recommendations)
    
    def generate_daily_message(self):
        """生成每日推送消息"""
        try:
            # 获取当前时间
            now = datetime.now(pytz.timezone('Asia/Shanghai'))
            date_str = now.strftime('%Y年%m月%d日')
            
            # 获取当前星期
            weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
            current_weekday = weekdays[now.weekday()]
            
            # 检查是否为工作日（周一到周五）
            if now.weekday() >= 5:  # 周六(5)和周日(6)
                return None  # 非工作日不推送
            
            # 获取天气信息
            weather_info = self.get_weather_info()
            
            # 获取今日运势
            today_fortune = self.get_today_fortune()
            
            # 获取午餐推荐
            lunch_recommendation = self.get_lunch_recommendation(weather_info)
            
            
            # 根据工作日生成哄用户上班的话语
            work_encouragement = self.get_work_encouragement(current_weekday)
            
            # 组合消息
            message = f"""💼 {work_encouragement}

🔮 今日运势（<a href="{os.getenv('FORTUNE_LINK_URL', 'http://localhost:5000')}">查看详情</a>）
{today_fortune}

🌤️ {weather_info}

🍽️ 午餐推荐：{lunch_recommendation}

祝大家今天也要开心摸鱼哦~ 🐟✨"""
            
            return message
            
        except Exception as e:
            logger.error(f"生成每日消息失败: {str(e)}")
            return "今日播报生成失败，但不影响大家继续摸鱼！ 🐟"
    
    def _sanitize_message(self, message):
        """清理和验证消息内容"""
        if not isinstance(message, str):
            message = str(message)
        
        # 移除潜在的敏感信息模式
        import re
        # 移除可能的API密钥、密码等敏感信息
        sensitive_patterns = [
            r'(?i)(api[_-]?key|password|token|secret)[\s=:]+[\w\-\.]+',
            r'(?i)(key|pwd|pass)[\s=:]+[\w\-\.]+'
        ]
        
        for pattern in sensitive_patterns:
            message = re.sub(pattern, '[REDACTED]', message)
        
        # 限制消息长度
        max_length = 4000  # 企业微信消息长度限制
        if len(message) > max_length:
            message = message[:max_length-10] + "...[截断]"
        
        return message
    
    def send_message(self, content):
        """发送消息到企业微信群"""
        if not self.webhook_url:
            logger.error("Webhook URL 未配置")
            return False
        
        # 清理和验证消息
        sanitized_content = self._sanitize_message(content)
            
        try:
            data = {
                "msgtype": "text",
                "text": {
                    "content": sanitized_content
                }
            }
            
            response = self._retry_request(requests.post, self.webhook_url, json=data, timeout=10)
            
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
    
    def send_daily_message(self):
        """发送每日消息"""
        logger.info("开始发送每日消息")
        message = self.generate_daily_message()
        if message is None:
            logger.info("今天是周末，跳过消息推送")
            return
        success = self.send_message(message)
        if success:
            logger.info("每日消息发送成功")
        else:
            logger.error("每日消息发送失败")


# 创建机器人实例
bot = None

def get_bot_instance():
    """获取机器人实例，延迟初始化"""
    global bot
    if bot is None:
        bot = WeWorkBot()
    return bot

# 在模块导入时创建实例
try:
    bot = WeWorkBot()
except Exception as e:
    logger.error(f"机器人初始化失败: {str(e)}")
    bot = None

# 注册API蓝图
from api import api_bp
app.register_blueprint(api_bp)

@app.route('/')
def root():
    """根路径 - 返回运势查看界面"""
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        from flask import redirect
        return redirect('/api/')

@app.route('/api/')
def index():
    """主页 - 返回运势查看界面"""
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return jsonify({
            'status': 'ok',
            'message': '企业微信群机器人运行中',
            'api_docs': '/api',
            'health_check': '/api/health',
            'endpoints': {
                'send': '/api/message/send (POST)',
                'send_daily': '/api/message/send-daily (POST)',
                'preview_daily': '/api/message/preview-daily (GET)',
                'weather': '/api/weather (GET)',
                'fortune': '/api/fortune (GET)',
                'constellation': '/api/constellation (GET)'
            }
        })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)