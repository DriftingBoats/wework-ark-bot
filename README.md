# 企业微信群机器人 - 定时推送版本

## 功能说明

这是一个企业微信群机器人的定时推送版本，主要功能包括：

- ⏰ **定时推送**：每天11:30自动推送消息
- 🌤️ **天气播报**：获取当天天气信息
- 🤖 **AI生成内容**：使用大模型生成幽默话语和午餐推荐，内容更加丰富多样
- 😄 **幽默话语**：戏谑幽默的将公司干倒闭的话语
- 🍽️ **午餐推荐**：根据当天天气推荐午饭
- 🔄 **降级机制**：AI不可用时自动使用预设文案

## 文件说明

- `wework_bot.py` - 新的定时推送机器人主程序
- `wework_bot_backup.py` - 原始版本的备份
- `api/index.py` - Vercel部署接口
- `requirements.txt` - 依赖包列表
- `vercel.json` - Vercel部署配置

## 环境变量配置

创建 `.env` 文件（参考 `.env.example`）：

```bash
# 企业微信群机器人配置
WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=your_webhook_key_here

# ARK API配置（用于AI生成内容）
ARK_API_KEY=your_ark_api_key_here
ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3

# 天气API配置（高德地图API）
CITY=北京
WEATHER_API_KEY=your_amap_api_key_here

# 服务器配置
PORT=5000
```

### 配置说明

- `WEBHOOK_URL`：企业微信群机器人的webhook地址（必需）
- `ARK_API_KEY`：Volces Engine ARK API密钥（可选，用于AI生成内容）
- `ARK_BASE_URL`：ARK API基础URL（可选，默认为火山引擎地址）
- `CITY`：城市名称，用于天气播报（可选，默认北京）
- `WEATHER_API_KEY`：高德地图API密钥（可选，用于获取真实天气数据）
- `PORT`：服务器端口（可选，默认5000）

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行方式

### 本地运行

```bash
python wework_bot.py
```

### Vercel部署

1. 将代码推送到GitHub
2. 在Vercel中导入项目
3. 配置环境变量
4. 部署完成

## API接口

### 1. 健康检查
```
GET /
```

### 2. 手动发送消息
```
POST /send
Content-Type: application/json

{
  "content": "要发送的消息内容"
}
```

### 3. 立即发送每日消息（测试用）
```
POST /send-daily
```

### 4. 预览每日消息内容
```
GET /preview-daily
```

## 定时任务

机器人会在每天11:30自动发送包含以下内容的消息：

1. **日期播报** - 当前日期
2. **天气信息** - 当天天气状况和温度
3. **幽默话语** - 随机选择的戏谑公司话语
4. **午餐推荐** - 根据天气推荐的午餐

## 消息示例

```
📅 2024年01月15日 每日播报

🌤️ 今日北京天气：晴天 25°C，阳光明媚

😄 今天又是努力让公司破产的一天！大家加油，争取早日实现财务自由（通过公司倒闭赔偿）💸

🍽️ 午餐推荐：晴天适合吃点清爽的：凉面、沙拉、寿司 🍱

祝大家今天也要开心摸鱼哦~ 🐟✨
```

## 自定义配置

### 修改推送时间

在 `wework_bot.py` 中修改：
```python
schedule.every().day.at("11:30").do(self.send_daily_message)
```

### 配置AI生成功能

1. **获取ARK API密钥**：
   - 访问 [火山引擎ARK平台](https://console.volcengine.com/ark)
   - 创建应用并获取API密钥
   - 在 `.env` 文件中配置 `ARK_API_KEY`

2. **AI生成逻辑**：
   - 优先使用AI生成幽默话语和午餐推荐
   - AI不可用时自动降级到预设文案
   - 可在 `call_ark_api` 方法中调整模型参数

### 添加更多幽默话语

在 `get_funny_bankruptcy_message` 方法的降级文案中添加更多内容到 `messages` 列表。

### 添加午餐推荐

在 `get_lunch_recommendation` 方法的降级文案中为不同天气添加更多推荐。

### 配置高德天气API

1. **获取高德API密钥**：
   - 访问 [高德开放平台](https://lbs.amap.com/)
   - 注册账号并创建应用
   - 获取Web服务API密钥
   - 在 `.env` 文件中配置 `WEATHER_API_KEY`

2. **API功能说明**：
   - 自动获取实时天气数据
   - 包含温度、天气状况、风力、湿度等信息
   - API不可用时自动降级到模拟数据
   - 支持全国主要城市查询

3. **城市配置**：
   - 支持中文城市名（如：北京、上海、广州）
   - 支持城市编码（如：110100）
   - 支持区县级别（如：朝阳区、浦东新区）

## 注意事项

1. 确保企业微信群机器人webhook地址正确配置
2. 定时任务在服务启动后自动开始运行
3. 如果部署在Vercel等无服务器平台，定时任务可能需要外部触发
4. 当前天气信息使用模拟数据，可根据需要接入真实API

## 故障排除

### 消息发送失败
- 检查WEBHOOK_URL是否正确
- 确认企业微信群机器人是否正常
- 查看日志输出的错误信息

### 定时任务不工作
- 确认服务是否持续运行
- 检查系统时区设置
- 查看日志确认定时任务是否启动

## 版本历史

- v2.0 - 定时推送版本，添加天气、幽默话语和午餐推荐功能
- v1.0 - 原始版本（已备份为 wework_bot_backup.py）