# 🤖 企业微信群机器人

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

一个功能丰富的企业微信群机器人，支持定时发送每日消息，集成AI生成内容，包含天气信息、老黄历运势、搞笑内容和午餐推荐。

## 🎯 项目亮点

- **🚀 Docker部署**：支持Docker容器化部署，易于管理和扩展
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
│   └── 📄 index.py           # 🚀 API接口定义
├── 📄 requirements.txt       # 📦 Python依赖包列表
├── 📄 .env.example          # 🔑 环境变量配置示例
├── 📄 .gitignore            # 🚫 Git忽略文件配置
└── 📄 README.md             # 📖 项目文档（当前文件）
```

### 核心文件说明
- **`wework_bot.py`** - 机器人主程序，包含Flask应用、定时任务、消息生成等所有功能
- **`index.html`** - 主页界面，提供老黄历和星座运势的可视化展示
- **`api/index.py`** - Web API接口，提供项目信息展示

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

# 定时任务配置（可选）
# Cron表达式格式：分 时 日 月 周
# 默认：每周一到周五上午10点执行
CRON_SCHEDULE=0 10 * * 1-5
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
| `CRON_SCHEDULE` | ⚪ 可选 | 定时任务执行时间 | 默认每周一到周五上午10点 |

### 🎯 配置优先级

- **最小配置**：仅需 `WEBHOOK_URL`，其他功能使用模拟数据
- **推荐配置**：添加 `WEATHER_API_KEY` 和 `TIANAPI_KEY`，获得真实数据
- **完整配置**：再添加 `ARK_API_KEY`，启用AI生成功能

## 🚀 部署指南

### 方式一：Docker 部署（推荐）

#### 环境要求
- Linux 系统（支持 Ubuntu、CentOS、Fedora、Arch 等）
- Docker Engine
- Git（可选，用于代码更新）

#### 快速部署步骤

**1. 安装 Docker**
```bash
# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 添加用户到 docker 组
sudo usermod -aG docker $USER
newgrp docker

# 验证安装
docker --version
```

**2. 克隆项目并配置**
```bash
# 克隆项目
git clone https://github.com/DriftingBoats/wework-bot.git
cd wework-bot

# 配置环境变量
cp .env.example .env
nano .env  # 编辑配置
```

**3. 一键部署**
```bash
# 给脚本执行权限
chmod +x deploy.sh

# 构建镜像
./deploy.sh build

# 启动服务
./deploy.sh start

# 验证部署
./deploy.sh status
curl http://localhost:5000/api/health/
```

**4. 设置定时任务**
```bash
# 使用脚本自动安装
./deploy.sh install-cron

# 或手动编辑 crontab
crontab -e
# 添加：0 10 * * 1-5 curl -X POST http://localhost:5000/api/message/send-daily
```

**5. 设置开机自启动（可选）**
```bash
# 设置开机自启动
./deploy.sh autostart

# 移除开机自启动
./deploy.sh remove-autostart

# 查看服务状态
sudo systemctl status wework-bot
```

#### Docker 管理命令

**使用部署脚本管理（推荐）**
```bash
# 构建镜像
./deploy.sh build

# 启动服务
./deploy.sh start

# 停止服务
./deploy.sh stop

# 重启服务
./deploy.sh restart

# 更新服务（重新构建并重启）
./deploy.sh update

# 查看状态
./deploy.sh status

# 查看日志
./deploy.sh logs

# 安装定时任务
./deploy.sh install-cron

# 设置开机自启动
./deploy.sh autostart

# 移除开机自启动
./deploy.sh remove-autostart

# 清理资源
./deploy.sh cleanup
```

**直接使用 Docker 命令**
```bash
# 查看容器状态
docker ps -a | grep wework-bot

# 查看实时日志
docker logs -f wework-bot

# 重启容器
docker restart wework-bot

# 停止容器
docker stop wework-bot

# 删除容器
docker rm wework-bot

# 重新构建镜像
docker build -t wework-bot .
```


### 方式二：本地开发

#### 环境准备
```bash
# 克隆项目
git clone https://github.com/DriftingBoats/wework-bot.git
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
- **默认时间**：每个工作日 10:00（北京时间）
- **推送范围**：周一至周五
- **节假日**：自动跳过（基于系统日历）

### 📝 消息内容
机器人每日推送包含以下模块：

1. **🤖 AI动态开场白** - 基于日期和星期智能生成
2. **🌤️ 天气信息** - 实时天气状况、温度、生活指数
3. **📅 今日运势** - 老黄历宜忌、冲煞（现代化表达）
4. **🍽️ 午餐推荐** - 根据天气和时节的智能推荐

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

通过 cron 配置定时任务：
```bash
# 编辑 crontab
crontab -e

# 添加定时任务（每天上午10:00发送）
0 10 * * 1-5 curl -X POST http://localhost:5000/api/message/send-daily

# 或使用部署脚本安装
./deploy.sh install-cron
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
2. 定时任务通过系统 cron 服务实现，需要手动配置
3. 确保服务持续运行以响应 cron 调用
4. 当前天气信息使用模拟数据，可根据需要接入真实API

## 🧪 测试功能

### API 测试命令
```bash
# 测试每日消息
curl -X POST http://localhost:5000/api/message/send-daily

# 测试预览消息
curl -X GET http://localhost:5000/api/message/preview-daily

# 发送自定义消息
curl -X POST http://localhost:5000/api/message/send \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello from WeWork Bot!"}'

# 健康检查
curl http://localhost:5000/api/health/

# 获取老黄历
curl http://localhost:5000/api/fortune

# 获取星座运势
curl http://localhost:5000/api/constellation?sign=leo
```

## 🛠️ 故障排除

### 服务无法启动
```bash
# 查看详细错误信息
./deploy.sh logs

# 检查配置文件
cat .env

# 检查端口占用
sudo netstat -tlnp | grep :5000
```

### 消息发送失败
1. **检查配置**：
   - 确认 `WEBHOOK_URL` 是否正确
   - 验证企业微信群机器人是否正常
2. **查看日志**：
   ```bash
   ./deploy.sh logs
   ```
3. **测试连接**：
   ```bash
   curl -X POST "$WEBHOOK_URL" \
     -H "Content-Type: application/json" \
     -d '{"msgtype": "text", "text": {"content": "测试消息"}}'
   ```

### 定时任务不工作
1. **检查 crontab 配置**：
   ```bash
   crontab -l
   ```
2. **查看 cron 日志**：
   ```bash
   sudo tail -f /var/log/cron
   ```
3. **手动测试 API**：
   ```bash
   curl -X POST http://localhost:5000/api/message/send-daily
   ```
4. **确认服务状态**：
   ```bash
   ./deploy.sh status
   ```
5. **重新安装 cron 任务**：
   ```bash
   ./deploy.sh install-cron
   ```

### 开机自启动问题
1. **检查 systemd 服务状态**：
   ```bash
   sudo systemctl status wework-bot
   ```
2. **查看服务日志**：
   ```bash
   sudo journalctl -u wework-bot -f
   ```
3. **重新设置自启动**：
   ```bash
   ./deploy.sh remove-autostart
   ./deploy.sh autostart
   ```
4. **手动启动服务**：
   ```bash
   sudo systemctl start wework-bot
   ```

### Docker 相关问题

**问题：容器启动失败**
```bash
# 查看详细错误信息
docker logs wework-bot

# 检查配置文件
cat .env
```

**问题：端口被占用**
```bash
# Linux 查看端口占用
lsof -i :5000

# 修改端口映射（编辑 docker-compose.yml）
ports:
  - "8080:5000"  # 改为其他端口
```

**问题：权限错误**
```bash
# 给予执行权限
chmod +x deploy.sh

# 检查 Docker 权限
sudo usermod -aG docker $USER
# 重新登录或重启
```

### 重置服务
```bash
# 完全重置（删除所有容器和镜像）
./deploy.sh cleanup
docker system prune -a

# 重新构建和启动
./deploy.sh build
./deploy.sh start
```

## ⚙️ 高级配置

### 自定义消息模板

编辑 `templates/` 目录下的模板文件：

```bash
# 编辑每日消息模板
nano templates/daily_message.txt

# 编辑老黄历模板
nano templates/fortune_template.txt
```

### 环境变量详细说明

```bash
# 企业微信配置
WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY

# 服务配置
PORT=5000                    # 服务端口
HOST=0.0.0.0                # 监听地址
DEBUG=false                 # 调试模式

# 消息配置
DAILY_MESSAGE_TIME=09:00    # 每日消息发送时间
WEEKEND_ENABLED=false       # 是否在周末发送

# API 配置
API_RATE_LIMIT=100          # API 请求限制
CACHE_TIMEOUT=3600          # 缓存超时时间

# 日志配置
LOG_LEVEL=INFO              # 日志级别
LOG_FILE=/app/logs/app.log  # 日志文件路径
```

### Docker Compose 高级配置

创建 `docker-compose.override.yml` 进行自定义配置：

```yaml
version: '3.8'
services:
  wework-bot:
    environment:
      - LOG_LEVEL=DEBUG
    volumes:
      - ./custom_templates:/app/templates
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/health/"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## 📊 监控和维护

### 日志管理

```bash
# 查看实时日志
./deploy.sh logs

# 查看最近 100 行日志
docker logs --tail 100 wework-bot

# 查看特定时间段的日志
docker logs --since="2024-01-01T00:00:00" --until="2024-01-02T00:00:00" wework-bot

# 日志轮转（防止日志文件过大）
sudo logrotate -f /etc/logrotate.d/docker-container
```

### 性能监控

```bash
# 查看容器资源使用情况
docker stats wework-bot

# 查看系统资源
top
htop
df -h
```

### 备份和恢复

```bash
# 备份配置文件
cp .env .env.backup.$(date +%Y%m%d)

# 备份自定义模板
tar -czf templates_backup_$(date +%Y%m%d).tar.gz templates/

# 导出 Docker 镜像
docker save wework-bot:latest | gzip > wework-bot-backup.tar.gz

# 恢复镜像
docker load < wework-bot-backup.tar.gz
```

## 🔒 安全建议

### 网络安全

1. **防火墙配置**：
   ```bash
   # 只允许本地访问
   sudo ufw allow from 127.0.0.1 to any port 5000
   
   # 或者允许特定 IP 段
   sudo ufw allow from 192.168.1.0/24 to any port 5000
   ```

2. **反向代理**（推荐使用 Nginx）：
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

### 数据安全

1. **环境变量保护**：
   ```bash
   # 设置文件权限
   chmod 600 .env
   
   # 避免将 .env 提交到版本控制
   echo ".env" >> .gitignore
   ```

2. **定期更新**：
   ```bash
   # 更新系统包
   sudo apt update && sudo apt upgrade
   
   # 更新 Docker
   sudo apt update docker-ce
   
   # 更新项目代码
   git pull origin main
   ./deploy.sh update
   ```

## 🚀 性能优化

### 容器优化

```yaml
# docker-compose.yml 性能优化
version: '3.8'
services:
  wework-bot:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 系统优化

```bash
# 清理 Docker 缓存
docker system prune -f

# 清理未使用的镜像
docker image prune -a

# 设置 Docker 日志轮转
sudo tee /etc/docker/daemon.json > /dev/null <<EOF
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF

sudo systemctl restart docker
```

## 🏭 生产环境部署

### 推荐配置

1. **服务器要求**：
   - CPU: 1 核心以上
   - 内存: 1GB 以上
   - 存储: 10GB 以上
   - 网络: 稳定的互联网连接

2. **系统配置**：
   ```bash
   # 设置时区
   sudo timedatectl set-timezone Asia/Shanghai
   
   # 配置 NTP 同步
   sudo systemctl enable systemd-timesyncd
   sudo systemctl start systemd-timesyncd
   
   # 设置系统限制
   echo "* soft nofile 65536" | sudo tee -a /etc/security/limits.conf
   echo "* hard nofile 65536" | sudo tee -a /etc/security/limits.conf
   ```

3. **自动启动配置**：
   ```bash
   # 创建 systemd 服务
   sudo tee /etc/systemd/system/wework-bot.service > /dev/null <<EOF
   [Unit]
   Description=WeWork Bot Service
   Requires=docker.service
   After=docker.service
   
   [Service]
   Type=oneshot
   RemainAfterExit=yes
   WorkingDirectory=/path/to/wework-ark-bot
   ExecStart=/path/to/wework-ark-bot/deploy.sh start
   ExecStop=/path/to/wework-ark-bot/deploy.sh stop
   
   [Install]
   WantedBy=multi-user.target
   EOF
   
   # 启用服务
   sudo systemctl enable wework-bot.service
   sudo systemctl start wework-bot.service
   ```

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


## 📞 联系方式

如有问题或建议，欢迎通过以下方式联系：

- 📧 Email: your-email@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/DriftingBoats/wework-bot/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/DriftingBoats/wework-bot/discussions)

---

⭐ 如果这个项目对你有帮助，请给个Star支持一下！