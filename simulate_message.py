#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import random
import requests
import json
from datetime import datetime
import pytz
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def get_weather_info():
    """获取天气信息"""
    weather_api_key = os.getenv('WEATHER_API_KEY')
    city = os.getenv('CITY', '上海')
    
    # 优先使用高德天气API
    if weather_api_key:
        weather_data = get_amap_weather(weather_api_key, city)
        if weather_data:
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
    return f"今日{city}天气：{weather['condition']} {weather['temp']}，{weather['desc']}"

def get_amap_weather(api_key, city):
    """使用高德API获取天气信息（包含当前温度、最高最低温度）"""
    try:
        # 先获取实况天气（当前温度）
        current_weather = get_amap_current_weather(api_key, city)
        
        # 再获取预报天气（最高最低温度）
        forecast_weather = get_amap_forecast_weather(api_key, city)
        
        if current_weather and forecast_weather:
            return f"{current_weather}，{forecast_weather}"
        elif current_weather:
            return current_weather
        elif forecast_weather:
            return forecast_weather
        else:
            return None
            
    except Exception as e:
        print(f"获取高德天气数据失败: {str(e)}")
        return None

def get_amap_current_weather(api_key, city):
    """获取高德实况天气"""
    try:
        url = "https://restapi.amap.com/v3/weather/weatherInfo"
        params = {
            'key': api_key,
            'city': city,
            'extensions': 'base'  # 实况天气
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('status') == '1' and data.get('lives'):
            live_data = data['lives'][0]
            city_name = live_data.get('city', city)
            weather = live_data.get('weather', '未知')
            temperature = live_data.get('temperature', '未知')
            winddirection = live_data.get('winddirection', '')
            windpower = live_data.get('windpower', '')
            humidity = live_data.get('humidity', '')
            
            # 获取当前星期
            now = datetime.now(pytz.timezone('Asia/Shanghai'))
            weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
            current_weekday = weekdays[now.weekday()]
            
            # 格式化天气信息
            weather_info = f"今日{city_name}天气（{current_weekday}）：{weather} {temperature}°C"
            
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
            print(f"高德实况天气API返回错误: {data.get('info', '未知错误')}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"高德实况天气API请求失败: {str(e)}")
        return None
    except Exception as e:
        print(f"解析高德实况天气数据失败: {str(e)}")
        return None

def get_amap_forecast_weather(api_key, city):
    """获取高德预报天气（最高最低温度）"""
    try:
        url = "https://restapi.amap.com/v3/weather/weatherInfo"
        params = {
            'key': api_key,
            'city': city,
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
                    
        print(f"高德预报天气API返回错误: {data.get('info', '未知错误')}")
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"高德预报天气API请求失败: {str(e)}")
        return None
    except Exception as e:
        print(f"解析高德预报天气数据失败: {str(e)}")
        return None

def get_funny_bankruptcy_message():
    """生成戏谑幽默的将公司干倒闭的话语"""
    ark_api_key = os.getenv('ARK_API_KEY')
    
    # 获取当前星期
    now = datetime.now(pytz.timezone('Asia/Shanghai'))
    weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    current_weekday = weekdays[now.weekday()]
    
    # 优先使用ARK API生成幽默话语
    if ark_api_key:
        ai_message = call_ark_api_for_humor(ark_api_key, current_weekday)
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

def call_ark_api(api_key, prompt, max_tokens=100, temperature=0.7):
    """通用ARK API调用函数"""
    try:
        url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        data = {
            "model": "deepseek-v3-250324",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        if result.get('choices') and len(result['choices']) > 0:
            content = result['choices'][0]['message']['content'].strip()
            return content
        else:
            print("ARK API返回格式异常")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"ARK API请求失败: {str(e)}")
        return None
    except Exception as e:
        print(f"解析ARK API响应失败: {str(e)}")
        return None

def call_ark_api_for_humor(api_key, current_weekday):
    """调用ARK API生成幽默话语"""
    # 使用更丰富的提示词，让每次生成都不同
    humor_themes = [
        f"今天是{current_weekday}，请结合这个星期特点生成一句关于上班摸鱼的幽默话语",
        "今天是{current_weekday}，请以'据可靠消息'开头，编一个关于老板或公司的搞笑传言",
        "今天是{current_weekday}，请模仿新闻播报的语气，播报一条关于员工摸鱼的'重大新闻'",
        "今天是{current_weekday}，请以'温馨提示'开头，提醒大家今天的摸鱼注意事项",
        "今天是{current_weekday}，请编一个关于工作效率和公司倒闭之间关系的搞笑统计数据",
        "今天是{current_weekday}，请以'最新研究表明'开头，发布一个关于摸鱼的'科学发现'",
        "今天是{current_weekday}，请模仿天气预报的语气，播报今天的'摸鱼指数'",
        "今天是{current_weekday}，请编一个关于KPI完成情况的搞笑总结"
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
    
    return call_ark_api(api_key, prompt, max_tokens=200, temperature=0.9)

def get_lunch_recommendation(weather_info):
    """根据天气推荐午餐"""
    ark_api_key = os.getenv('ARK_API_KEY')
    
    # 优先使用ARK API生成推荐
    if ark_api_key:
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
        
        ai_recommendation = call_ark_api(ark_api_key, prompt, max_tokens=150, temperature=0.8)
        if ai_recommendation:
            return ai_recommendation
    
    # 降级到基于天气的固定推荐
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



def generate_daily_message():
    """生成每日推送消息"""
    # 获取当前时间
    now = datetime.now(pytz.timezone('Asia/Shanghai'))
    date_str = now.strftime('%Y年%m月%d日')
    
    # 获取当前星期
    weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    current_weekday = weekdays[now.weekday()]
    
    # 检查是否为工作日（周一到周五）
    if now.weekday() >= 5:  # 周六(5)和周日(6)
        print(f"今天是{current_weekday}，非工作日不推送消息")
        return None  # 非工作日不推送
    
    # 获取天气信息
    weather_info = get_weather_info()
    
    # 获取幽默话语
    funny_message = get_funny_bankruptcy_message()
    
    # 获取午餐推荐
    lunch_recommendation = get_lunch_recommendation(weather_info)
    
    # 组合消息
    message = f"""📅 {date_str} {current_weekday}

🌤️ {weather_info}

😄 {funny_message}

🍽️ 午餐推荐：{lunch_recommendation}

祝大家今天也要开心摸鱼哦~ 🐟✨"""
    
    return message

if __name__ == "__main__":
    print("=== 模拟生成每日文案 ===")
    print()
    message = generate_daily_message()
    if message is None:
        print("今天是周末，不推送消息")
    else:
        print(message)
    print()
    print("=== 文案生成完成 ===")