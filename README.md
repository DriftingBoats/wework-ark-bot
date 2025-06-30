# 🤖 企业微信群机器人

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/your-username/wework-ark-bot)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

一个功能丰富的企业微信群机器人，支持定时发送每日消息，集成AI生成内容，包含天气信息、老黄历运势、搞笑内容和午餐推荐。

## 🎯 项目亮点

- **🚀 一键部署**：支持Vercel无服务器部署，零运维成本
- **🤖 AI驱动**：集成火山引擎ARK API，动态生成个性化内容
- **📱 企业级**：专为企业微信群设计，提升团队氛围
- **⚡ 高性能**：智能缓存机制，API重试策略，确保稳定运行
- **🔧 易配置**：环境变量配置，支持多种API服务商

## ✨ 功能特性

### 📱 核心功能
- 🌤️ **智能天气播报**：集成高德地图API，提供实时天气信息和生活指数
- 📅 **传统运势解读**：老黄历信息，包含宜忌、冲煞，以现代化方式呈现
- ⭐ **星座运势查询**：支持12星座运势查询，集成天行数据API
- 🏠 **可视化主页**：美观的Web界面，实时显示老黄历和星座运势
- 🤖 **AI动态开场白**：基于日期和星期智能生成个性化问候语
- 😄 **幽默破产文学**：每日精选搞笑内容，缓解工作压力
- 🍽️ **智能午餐推荐**：根据天气和时节推荐合适的午餐选择

### ⚙️ 技术特性
- ⏰ **精准定时推送**：工作日自动推送（北京时间12:30），支持自定义时间
- 🔧 **灵活手动触发**：支持API接口手动发送消息和预览内容
- 📊 **完善监控体系**：健康检查、状态监控、错误追踪
- 🚀 **企业级性能**：
  - 🧠 智能缓存机制（天气1小时，运势12小时）
  - 🔄 API请求重试机制，确保消息送达
  - 🛡️ 输入验证和安全过滤
  - 📈 性能监控和日志记录
  - 🎯 优雅降级策略，API失败时使用备用内容

## 📁 项目结构

```
wework-ark-bot/
├── 📄 wework_bot.py          # 🤖 机器人主程序，包含所有核心功能
├── 📄 index.html             # 🏠 主页界面，显示老黄历和星座运势
├── 📁 api/
│   └── 📄 index.py           # 🚀 Vercel部署入口，API接口定义
├── 📁 .github/
│   └── 📁 workflows/         # ⚙️ GitHub Actions自动化工作流
├── 📄 requirements.txt       # 📦 Python依赖包列表
├── 📄 vercel.json           # 🔧 Vercel部署配置文件
├── 📄 .env.example          # 🔑 环境变量配置示例
├── 📄 .gitignore            # 🚫 Git忽略文件配置
└── 📄 README.md             # 📖 项目文档（当前文件）
```

### 核心文件说明
- **`wework_bot.py`** - 机器人主程序，包含Flask应用、定时任务、消息生成等所有功能
- **`index.html`** - 主页界面，提供老黄历和星座运势的可视化展示
- **`api/index.py`** - Vercel部署接口，提供Web API和项目信息展示
- **`.github/workflows/`** - GitHub Actions工作流，支持自动化部署和定时触发

## 🔧 环境变量配置

### 快速开始

1. 复制环境变量模板：
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，填入真实配置：

```bash
# ===== 必需配置 =====
# 企业微信群机器人Webhook URL（必需）
WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=your_webhook_key

# ===== 可选配置 =====
# 高德地图API密钥（推荐配置，用于获取真实天气）
WEATHER_API_KEY=your_amap_api_key

# 天行数据API密钥（推荐配置，用于获取老黄历）
TIANAPI_KEY=your_tianapi_key

# 火山引擎ARK API配置（推荐配置，用于AI生成内容）
ARK_API_KEY=your_ark_api_key
ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3

# 城市配置（可选，默认上海）
CITY=上海
```

### 📋 详细配置说明

| 配置项 | 必需性 | 说明 | 获取方式 |
|--------|--------|------|----------|
| `WEBHOOK_URL` | ✅ 必需 | 企业微信群机器人的webhook地址 | [企业微信管理后台](https://work.weixin.qq.com/) → 应用管理 → 群机器人 |
| `WEATHER_API_KEY` | 🔶 推荐 | 高德地图API密钥，用于获取真实天气 | [高德开放平台](https://lbs.amap.com/) |
| `TIANAPI_KEY` | 🔶 推荐 | 天行数据API密钥，用于获取老黄历 | [天行数据](https://www.tianapi.com/) |
| `ARK_API_KEY` | 🔶 推荐 | 火山引擎ARK API密钥，用于AI生成 | [火山引擎ARK](https://console.volcengine.com/ark) |
| `ARK_BASE_URL` | ⚪ 可选 | ARK API基础URL | 默认火山引擎地址 |
| `CITY` | ⚪ 可选 | 城市名称，用于天气播报 | 默认上海，支持全国城市 |

### 🎯 配置优先级

- **最小配置**：仅需 `WEBHOOK_URL`，其他功能使用模拟数据
- **推荐配置**：添加 `WEATHER_API_KEY` 和 `TIANAPI_KEY`，获得真实数据
- **完整配置**：再添加 `ARK_API_KEY`，启用AI生成功能

## 🚀 部署指南

### 方式一：Vercel部署（推荐）

#### 一键部署
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/your-username/wework-ark-bot)

#### 手动部署
1. **Fork项目**：点击右上角Fork按钮
2. **导入Vercel**：
   - 访问 [Vercel](https://vercel.com/)
   - 点击 "New Project"
   - 选择你Fork的仓库
3. **配置环境变量**：
   - 在Vercel项目设置中添加环境变量
   - 至少配置 `WEBHOOK_URL`
4. **部署完成**：自动部署，获得访问链接

### 方式二：本地开发

#### 环境准备
```bash
# 克隆项目
git clone https://github.com/your-username/wework-ark-bot.git
cd wework-ark-bot

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件
```

#### 启动服务
```bash
# 启动机器人服务
python wework_bot.py

# 服务将在 http://localhost:5000 启动
# 定时任务自动开始运行
```

## 📡 API接口文档

### 接口概览

| 接口 | 方法 | 功能 | 说明 |
|------|------|------|------|
| `/` | GET | 项目信息 | 查看项目状态和API文档 |
| `/index.html` | GET | 主页界面 | 显示老黄历和星座运势 |
| `/status` | GET | 运行状态 | 机器人运行状态检查 |
| `/health` | GET | 健康检查 | 服务状态监控 |
| `/send` | POST | 手动发送 | 发送自定义消息到群 |
| `/send-daily` | POST | 发送日报 | 立即发送每日消息 |
| `/preview-daily` | GET | 预览日报 | 预览每日消息内容 |
| `/api/fortune` | GET | 老黄历API | 获取今日老黄历信息 |
| `/api/constellation` | GET | 星座运势API | 获取指定星座运势 |

### 详细接口说明

#### 1. 📊 项目信息
```http
GET /
```
**响应示例：**
```json
{
  "name": "企业微信群机器人",
  "version": "2.1.0",
  "status": "running",
  "features": [...],
  "api_endpoints": {...}
}
```

#### 2. 🏠 主页界面
```http
GET /index.html
```
**用途：** 访问可视化主页，显示老黄历和星座运势

#### 3. 💬 手动发送消息
```http
POST /send
Content-Type: application/json

{
  "content": "要发送的消息内容"
}
```

#### 4. 📅 立即发送每日消息
```http
POST /send-daily
```
**用途：** 测试功能，立即触发每日消息推送

#### 5. 👀 预览每日消息
```http
GET /preview-daily
```
**用途：** 预览今日消息内容，不发送到群

#### 6. 📅 获取老黄历信息
```http
GET /api/fortune
```
**响应示例：**
```json
{
  "data": "🌝 农历：乙巳年 六月初六\n✅ 宜：出行.会友.上书.见工\n❌ 忌：动土.破屋.伐木.安葬",
  "status": "success"
}
```

#### 7. ⭐ 获取星座运势
```http
GET /api/constellation?sign=leo
```
**参数说明：**
- `sign`: 星座名称（英文），支持12星座：aries, taurus, gemini, cancer, leo, virgo, libra, scorpio, sagittarius, capricorn, aquarius, pisces

**响应示例：**
```json
{
  "data": "⭐ 狮子座今日运势\n📅 日期：2025-06-30",
  "status": "success"
}
```

## ⏰ 定时任务

### 📅 推送时间
- **默认时间**：每个工作日 12:30（北京时间）
- **推送范围**：周一至周五
- **节假日**：自动跳过（基于系统日历）

### 📝 消息内容
机器人每日推送包含以下模块：

1. **🤖 AI动态开场白** - 基于日期和星期智能生成
2. **🌤️ 天气信息** - 实时天气状况、温度、生活指数
3. **📅 今日运势** - 老黄历宜忌、冲煞（现代化表达）
4. **😄 幽默内容** - 破产文学或AI生成的搞笑内容
5. **🍽️ 午餐推荐** - 根据天气和时节的智能推荐

## 📱 消息示例

### 完整版消息（启用所有API）
```
🌟 各位打工人，甲辰年冬月廿七的星期三来啦！
今天阳光正好，适合在办公室里做白日梦~ ✨

🌤️ 【天气播报】
上海今日：晴转多云 15°C~22°C
东南风2级，空气质量良好
紫外线指数：中等，建议防晒

📅 【今日运势】
宜：会友、出行、签约
忌：搬家、装修、投资
冲煞：冲狗(戊戌)煞南
💡 属狗的朋友今天要低调一些哦~

😄 【今日吐槽】
又是为公司贡献GDP的一天！
努力工作，争取让老板早日换新车 🚗💨

🍽️ 【午餐推荐】
天气不错，来点清爽的：
🥗 轻食沙拉 | 🍜 日式拉面 | 🍱 精致便当

愿大家今天都能愉快摸鱼，准时下班！🐟✨
```

### 精简版消息（仅基础配置）
```
📅 2024年12月25日（星期三）
预制人今日播报咯~

🌤️ 今日上海天气：晴天 20°C

😄 今天也是为了让公司破产而努力的一天！
大家加油，争取早日实现财务自由 💸

🍽️ 午餐推荐：天气不错，适合吃点清爽的

祝大家摸鱼愉快~ 🐟
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

## 📈 版本历史

### v2.1.0 (2024-12-25) - AI智能版
- ✨ 新增AI动态开场白生成功能
- 🎨 优化运势显示，农历格式现代化
- 🧹 简化冲煞信息，转换为大白话提醒
- 🗑️ 移除彭祖百忌显示，提升用户体验
- 📱 优化API接口展示页面
- 📚 完善项目文档和部署指南

### v2.0.0 (2024-12) - 定时推送版
- ⏰ 添加定时推送功能
- 🌤️ 集成天气播报（高德地图API）
- 📅 添加老黄历运势（天行数据API）
- 😄 添加幽默破产文学
- 🍽️ 智能午餐推荐
- 🚀 性能优化和缓存机制

### v1.0.0 (2024-11) - 基础版
- 🤖 基础企业微信机器人功能
- 💬 手动消息发送
- 🔧 简单配置管理

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

### 开发流程
1. Fork本项目
2. 创建功能分支：`git checkout -b feature/amazing-feature`
3. 提交更改：`git commit -m 'Add amazing feature'`
4. 推送分支：`git push origin feature/amazing-feature`
5. 提交Pull Request

### 代码规范
- 遵循PEP 8代码风格
- 添加必要的注释和文档
- 确保所有测试通过
- 更新相关文档

## 📄 许可证

本项目采用 [MIT License](https://opensource.org/licenses/MIT) 开源协议。

## 🙏 致谢

- [企业微信](https://work.weixin.qq.com/) - 提供机器人API
- [高德地图](https://lbs.amap.com/) - 天气数据服务
- [天行数据](https://www.tianapi.com/) - 老黄历数据服务
- [火山引擎ARK](https://console.volcengine.com/ark) - AI内容生成服务
- [Vercel](https://vercel.com/) - 免费部署平台

## 📞 联系方式

如有问题或建议，欢迎通过以下方式联系：

- 📧 Email: your-email@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/your-username/wework-ark-bot/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/your-username/wework-ark-bot/discussions)

---

⭐ 如果这个项目对你有帮助，请给个Star支持一下！