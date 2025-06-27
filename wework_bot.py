#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
企业微信群机器人 - 定时推送版本
每天11:30推送天气、幽默话语和午餐推荐
"""

import os
import os
import json
import random
import threading
import time
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from dotenv import load_dotenv
import requests
import schedule
import pytz
import logging

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class WeWorkBot:
    def __init__(self, start_scheduler=True):
        self.webhook_url = os.getenv('WEBHOOK_URL')
        self.weather_api_key = os.getenv('WEATHER_API_KEY')  # 可选的天气API密钥
        self.city = os.getenv('CITY', '上海')  # 默认城市
        self.ark_api_key = os.getenv('ARK_API_KEY')
        self.ark_base_url = os.getenv('ARK_BASE_URL', 'https://ark.cn-beijing.volces.com/api/v3')
        self.scheduler_started = False
        
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
        
        # 根据参数决定是否启动定时任务
        if start_scheduler:
            self.start_scheduler()
    
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
    
    def call_ark_api(self, prompt, max_tokens=200, temperature=0.8):
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
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'max_tokens': max_tokens,
                'temperature': temperature
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
                
                # 提取关键信息并格式化
                lunar_date = result.get('lunardate', '')
                lunar_day = result.get('lunarday', '')
                fitness = result.get('fitness', '无特别宜事')
                taboo = result.get('taboo', '无特别忌事')
                chongsha = result.get('chongsha', '')
                pengzu = result.get('pengzu', '')
                
                # 格式化运势信息
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
    
    def get_funny_bankruptcy_message(self):
        """生成戏谑幽默的将公司干倒闭的话语"""
        # 优先使用大模型生成
        if self.ark_api_key:
            # 获取当前星期
            from datetime import datetime
            import pytz
            now = datetime.now(pytz.timezone('Asia/Shanghai'))
            weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
            current_weekday = weekdays[now.weekday()]
            
            # 使用更丰富的提示词，让每次生成都不同
            humor_themes = [
                f"今天是{current_weekday}，请结合这个星期特点生成一句关于上班摸鱼的幽默话语",
                f"今天是{current_weekday}，请以'据可靠消息'开头，编一个关于老板或公司的搞笑传言",
                f"今天是{current_weekday}，请模仿新闻播报的语气，播报一条关于员工摸鱼的'重大新闻'",
                f"今天是{current_weekday}，请以'温馨提示'开头，提醒大家今天的摸鱼注意事项",
                f"今天是{current_weekday}，请编一个关于工作效率和公司倒闭之间关系的搞笑统计数据",
                f"今天是{current_weekday}，请以'最新研究表明'开头，发布一个关于摸鱼的'科学发现'",
                f"今天是{current_weekday}，请模仿天气预报的语气，播报今天的'摸鱼指数'",
                f"今天是{current_weekday}，请编一个关于KPI完成情况的搞笑总结"
            ]
            
            theme = random.choice(humor_themes)
            prompt = f"""{theme}。
            
要求：
1. 语言风趣幽默，带有自嘲和调侃色彩
2. 内容要丰富一些，可以2-3句话，让人看完会心一笑
3. 适合在工作群里发送，不要过分或冒犯
4. 多使用emoji表情增加趣味性
5. 要有创意，避免老套的说法
6. 可以适当夸张，但保持玩笑性质

请直接输出内容，不要解释。"""
            
            ai_message = self.call_ark_api(prompt, max_tokens=200, temperature=0.9)
            if ai_message:
                return ai_message
        
        # 降级到固定文案（更丰富有趣的版本）
        messages = [
            "📺 摸鱼新闻联播：据本台记者报道，今日全公司摸鱼指数再创新高，预计公司倒闭进度条已加载至85%。老板表示很欣慰，终于可以提前退休了 🐟📈",
            "🌡️ 今日摸鱼天气预报：上班热情持续走低，工作效率维持在冰点附近。建议大家做好保暖措施，以防被老板的怒火冻伤 ❄️😂",
            "📊 最新研究表明：员工每摸一次鱼，公司倒闭概率增加0.1%。按照目前的摸鱼频率，预计下周三公司就能成功破产，大家再接再厉！ 🔬📉",
            "🎯 温馨提示：今日KPI完成度为-50%，恭喜大家成功让公司业绩倒退到石器时代。考古学家已经在路上了 🏺⛏️",
            "📰 据可靠消息：老板昨晚做梦都在笑，因为终于找到了让公司快速倒闭的秘诀——雇佣我们这群'人才'。梦里他已经在马尔代夫晒太阳了 🏖️😎",
            "🏆 重大喜讯：经过全体员工的不懈努力，我们成功将'如何让公司破产'这门艺术发挥到了极致。预计很快就能获得'年度最佳倒闭团队'奖 🥇💸",
            "⚡ 突发新闻：公司账户余额与员工工作积极性发生了神奇的量子纠缠现象，两者同时趋近于零。物理学家表示这违反了能量守恒定律 🔬⚛️",
            "🎪 今日马戏团表演：观看员工如何在上班时间完美演绎'身在曹营心在汉'。门票免费，老板买单，欢迎围观！ 🎭🍿",
            "📈 股市分析：如果摸鱼也能上市，我们公司绝对是蓝筹股。建议大家抓紧时间投资，错过这村就没这店了！ 💰📊",
            "🔮 占卜预测：水晶球显示，按照目前的工作状态，公司将在农历七月十五成功转型为灵异主题乐园。门票已开始预售 👻🎢"
        ]
        return random.choice(messages)
    
    def generate_dynamic_greeting(self, date_str, current_weekday):
        """使用LLM生成动态开场白"""
        # 优先使用大模型生成
        if self.ark_api_key:
            # 根据不同星期和时间生成不同风格的开场白
            greeting_styles = [
                f"请为企业微信群机器人生成一个{current_weekday}的有趣开场白，日期是{date_str}",
                f"请以电台主播的语气，为{current_weekday}({date_str})生成一个幽默的开场白",
                f"请以摸鱼专家的身份，为{current_weekday}({date_str})写一个搞笑的问候语",
                f"请模仿新闻播报员，为{current_weekday}({date_str})生成一个有趣的开场白",
                f"请以打工人的角度，为{current_weekday}({date_str})写一个自嘲式的问候语",
                f"请以AI助手的身份，为{current_weekday}({date_str})生成一个温馨幽默的开场白"
            ]
            
            style = random.choice(greeting_styles)
            prompt = f"""{style}。
            
要求：
1. 语言风趣幽默，适合工作群聊
2. 长度控制在2-3句话
3. 要体现{current_weekday}的特点
4. 适当使用emoji表情
5. 语气要亲切友好
6. 可以结合摸鱼、打工等职场梗
7. 避免过于正式或严肃

请直接输出开场白内容，不要解释。"""
            
            ai_greeting = self.call_ark_api(prompt, max_tokens=100, temperature=0.9)
            if ai_greeting:
                return ai_greeting
        
        # 降级到固定开场白
        fallback_greetings = {
            '周一': f"🌅 {current_weekday}好！新的一周开始了，今天是{date_str}\n💪 充满希望的一周，让我们一起加油鸭~",
            '周二': f"⚡ {current_weekday}快乐！今天是{date_str}\n🎯 继续昨天的干劲，今天也要元气满满哦~",
            '周三': f"🎪 {current_weekday}好呀！今天是{date_str}\n📻 一周过半啦，坚持就是胜利，摸鱼电台继续陪伴大家~",
            '周四': f"🚀 {current_weekday}快乐！今天是{date_str}\n🌟 胜利在望的一天，明天就是快乐星期五啦~",
            '周五': f"🎉 终于到了快乐{current_weekday}！今天是{date_str}\n🍻 周末在向我们招手，今天让我们愉快地收尾这一周~",
            '周六': f"😴 美好的{current_weekday}！今天是{date_str}\n🛋️ 周末时光，是时候好好休息一下了~",
            '周日': f"☀️ 悠闲的{current_weekday}！今天是{date_str}\n📚 周末的最后一天，为新的一周做好准备吧~"
        }
        
        return fallback_greetings.get(current_weekday, f"🌈 {current_weekday}好！今天是{date_str}\n✨ 美好的一天开始了，让我们一起度过愉快的时光~")
    
    def get_lunch_recommendation(self, weather_info):
        """根据天气推荐午餐"""
        # 优先使用大模型生成
        if self.ark_api_key:
            # 使用更丰富的提示词模板
            recommendation_styles = [
                f"请以美食博主的语气，根据天气'{weather_info}'推荐今日午餐",
                f"请以营养师的专业角度，结合天气'{weather_info}'给出午餐建议",
                f"请以吃货的热情，根据天气'{weather_info}'安利一道必吃美食",
                f"请以厨师的创意思维，结合天气'{weather_info}'设计今日特色午餐",
                f"请以美食评论家的口吻，根据天气'{weather_info}'点评推荐午餐",
                f"请以朋友聊天的语气，根据天气'{weather_info}'分享午餐心得"
            ]
            
            style = random.choice(recommendation_styles)
            prompt = f"""{style}。
            
要求：
1. 内容要生动有趣，有画面感
2. 可以包含2-3句话，描述食物的诱人之处
3. 结合天气特点说明为什么适合
4. 语言要有感染力，让人看了就想吃
5. 适当使用emoji表情
6. 避免过于正式，要接地气

请直接输出推荐内容，不要解释。"""
            
            ai_recommendation = self.call_ark_api(prompt, max_tokens=150, temperature=0.8)
            if ai_recommendation:
                return ai_recommendation
        
        # 降级到固定文案
        if '晴' in weather_info or '阳光' in weather_info:
            recommendations = [
                "晴天适合吃点清爽的：凉面、沙拉、寿司 🍱",
                "阳光明媚，来份烤肉配冰饮料吧！ 🍖🥤",
                "好天气就要吃好的：日式料理或者韩式烤肉 🍣"
            ]
        elif '雨' in weather_info:
            recommendations = [
                "下雨天配热汤：麻辣烫、火锅、拉面 🍜",
                "雨天来碗热腾腾的粥配小菜 🍲",
                "下雨天最适合吃川菜，辣一点暖暖身子 🌶️"
            ]
        elif '阴' in weather_info or '云' in weather_info:
            recommendations = [
                "阴天适合中式家常菜：红烧肉、宫保鸡丁 🥘",
                "多云的天气来份盖浇饭或者炒饭 🍚",
                "阴天就吃点温和的：蒸蛋羹、小馄饨 🥟"
            ]
        elif '风' in weather_info:
            recommendations = [
                "大风天气要吃饱：汉堡、炸鸡、披萨 🍔",
                "风大适合吃热乎的：包子、饺子、煎饼 🥟",
                "刮风天来份重口味：麻辣香锅、水煮鱼 🐟"
            ]
        else:
            recommendations = [
                "今天就随便吃点：外卖、快餐、便当 🍱",
                "不知道吃什么？那就吃昨天想吃但没吃的 🤷",
                "午餐推荐：闭眼点外卖，吃什么都是缘分 🎲"
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
            
            # 获取幽默话语
            funny_message = self.get_funny_bankruptcy_message()
            
            # 获取午餐推荐
            lunch_recommendation = self.get_lunch_recommendation(weather_info)
            
            # 生成动态开场白
            greeting = self.generate_dynamic_greeting(date_str, current_weekday)
            
            # 组合消息
            message = f"""📻 {greeting}

{today_fortune}

🌤️ {weather_info}

😄 {funny_message}

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
    
    def start_scheduler(self):
        """启动定时任务"""
        if self.scheduler_started:
            logger.info("定时任务已经启动，跳过重复启动")
            return
            
        try:
            # 设置每天11:30发送消息
            schedule.every().day.at("11:30").do(self.send_daily_message)
            
            # 在后台线程中运行调度器
            def run_scheduler():
                while True:
                    schedule.run_pending()
                    time.sleep(60)  # 每分钟检查一次
            
            scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
            scheduler_thread.start()
            self.scheduler_started = True
            logger.info("定时任务已启动，每天11:30将自动发送消息")
        except Exception as e:
            logger.error(f"启动定时任务失败: {str(e)}")

# 创建机器人实例
# 检测是否在Vercel环境中运行
is_vercel = os.getenv('VERCEL') == '1' or os.getenv('VERCEL_ENV') is not None

bot = None

def get_bot_instance():
    """获取机器人实例，延迟初始化"""
    global bot
    if bot is None:
        # 在Vercel环境中不启动定时任务
        start_scheduler = not is_vercel
        bot = WeWorkBot(start_scheduler=start_scheduler)
    return bot

# 在模块导入时创建实例
try:
    # 在Vercel环境中不启动定时任务
    start_scheduler = not is_vercel
    bot = WeWorkBot(start_scheduler=start_scheduler)
    if is_vercel:
        logger.info("在Vercel环境中运行，定时任务已禁用")
except Exception as e:
    logger.error(f"机器人初始化失败: {str(e)}")
    bot = None

@app.route('/', methods=['GET'])
def index():
    """健康检查接口"""
    current_bot = get_bot_instance()
    if current_bot is None:
        return jsonify({
            'status': 'error',
            'message': '机器人初始化失败'
        }), 500
    
    return jsonify({
        'status': 'ok',
        'message': '企业微信群机器人运行中 - 定时推送版本',
        'webhook_configured': bool(current_bot.webhook_url),
        'city': current_bot.city,
        'next_schedule': '每天11:30自动推送'
    })

@app.route('/health')
def health_check():
    """健康检查接口"""
    bot = WeWorkBot()
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'wework-bot',
        'config': {
            'webhook_configured': bool(bot.webhook_url),
            'weather_api_configured': bool(bot.weather_api_key),
            'tianapi_configured': bool(os.getenv('TIANAPI_KEY')),
            'ark_api_configured': bool(bot.ark_api_key)
        },
        'cache_stats': {
            'cached_items': len(bot.cache),
            'cache_keys': list(bot.cache.keys())
        }
    }
    
    # 检查关键配置
    if not bot.webhook_url:
        health_status['status'] = 'warning'
        health_status['warnings'] = ['WEBHOOK_URL not configured']
    
    return jsonify(health_status)

@app.route('/send', methods=['POST'])
def send_message():
    """手动发送消息接口"""
    try:
        current_bot = get_bot_instance()
        if current_bot is None:
            return jsonify({'status': 'error', 'message': '机器人未初始化'}), 500
            
        data = request.get_json()
        content = data.get('content', '')
        
        if not content:
            return jsonify({'status': 'error', 'message': '消息内容不能为空'}), 400
        
        success = current_bot.send_message(content)
        
        if success:
            return jsonify({'status': 'success', 'message': '消息发送成功'})
        else:
            return jsonify({'status': 'error', 'message': '消息发送失败'}), 500
            
    except Exception as e:
        logger.error(f"发送消息异常: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/send-daily', methods=['POST'])
def send_daily_now():
    """立即发送每日消息（测试用）"""
    try:
        current_bot = get_bot_instance()
        if current_bot is None:
            return jsonify({'status': 'error', 'message': '机器人未初始化'}), 500
            
        current_bot.send_daily_message()
        return jsonify({'status': 'success', 'message': '每日消息已发送'})
    except Exception as e:
        logger.error(f"发送每日消息异常: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/preview-daily', methods=['GET'])
def preview_daily_message():
    """预览每日消息内容"""
    try:
        current_bot = get_bot_instance()
        if current_bot is None:
            return jsonify({'status': 'error', 'message': '机器人未初始化'}), 500
            
        message = current_bot.generate_daily_message()
        if message is None:
            return jsonify({'status': 'success', 'message': '今天是周末，不推送消息'})
        return jsonify({'status': 'success', 'message': message})
    except Exception as e:
        logger.error(f"预览每日消息异常: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)