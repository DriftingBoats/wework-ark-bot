# API 项目结构说明

## 概述

项目已经重构为模块化的API结构，将不同功能的API分别放在独立的模块中，提高了代码的可维护性和可扩展性。

## 目录结构

```
api/
├── __init__.py          # API模块初始化，注册所有蓝图
├── index.py             # WSGI应用入口点
├── health.py            # 健康检查API模块
├── weather.py           # 天气API模块
├── fortune.py           # 老黄历API模块
├── constellation.py     # 星座运势API模块
├── message.py           # 消息发送API模块
└── info.py              # 项目信息API模块
```

## API模块说明

### 1. 健康检查模块 (`health.py`)
- **路径前缀**: `/api/health`
- **功能**: 系统健康检查和状态监控
- **接口**:
  - `GET /api/health/` - 系统健康检查
  - `GET /api/health/status` - 系统状态信息

### 2. 天气模块 (`weather.py`)
- **路径前缀**: `/api/weather`
- **功能**: 天气信息查询
- **接口**:
  - `GET /api/weather/` - 获取天气信息
  - `GET /api/weather/current` - 获取当前天气
  - `GET /api/weather/forecast` - 获取天气预报

### 3. 老黄历模块 (`fortune.py`)
- **路径前缀**: `/api/fortune`
- **功能**: 老黄历信息查询
- **接口**:
  - `GET /api/fortune/` - 获取老黄历信息
  - `GET /api/fortune/today` - 获取今日老黄历
  - `GET /api/fortune/almanac` - 获取详细黄历信息
  - `GET /api/fortune/simple` - 获取简化老黄历

### 4. 星座运势模块 (`constellation.py`)
- **路径前缀**: `/api/constellation`
- **功能**: 星座运势查询
- **接口**:
  - `GET /api/constellation/` - 获取指定星座运势
  - `GET /api/constellation/list` - 获取支持的星座列表
  - `GET /api/constellation/today` - 获取今日星座运势
  - `POST /api/constellation/batch` - 批量获取星座运势

### 5. 消息发送模块 (`message.py`)
- **路径前缀**: `/api/message`
- **功能**: 消息发送和管理
- **接口**:
  - `POST /api/message/send` - 发送自定义消息
  - `POST /api/message/send-daily` - 发送每日消息
  - `GET /api/message/preview-daily` - 预览每日消息
  - `POST /api/message/send-weather` - 发送天气消息
  - `POST /api/message/send-fortune` - 发送老黄历消息
  - `POST /api/message/send-lunch` - 发送午餐推荐
  - `GET /api/message/templates` - 获取消息模板

### 6. 项目信息模块 (`info.py`)
- **路径前缀**: `/api`
- **功能**: 项目信息和文档
- **接口**:
  - `GET /api` - 项目主页
  - `GET /api/info` - 获取API信息和文档
  - `GET /api/version` - 获取版本信息
  - `GET /api/endpoints` - 获取所有API端点
  - `GET /api/stats` - 获取API统计信息

## 兼容性处理

为了保持向后兼容性，主应用文件 `wework_bot.py` 中保留了旧的路由，并将它们重定向到新的API路径：

- `/api/` → 项目主页
- `/api/status` → `/api/health` (状态检查)
- `/api/health-check` → `/api/health` (健康检查)
- `/api/send` → `/api/message/send` (发送消息)
- `/api/send-daily` → `/api/message/send-daily` (发送每日消息)
- `/api/preview-daily` → `/api/message/preview-daily` (预览每日消息)
- `/api/index.html` → 静态文件服务
- `/api/home` → 静态文件服务

## 使用示例

### 获取API信息
```bash
curl http://localhost:5000/api/info
```

### 获取健康检查
```bash
curl http://localhost:5000/api/health/
```

### 获取老黄历
```bash
curl http://localhost:5000/api/fortune/
```

### 获取星座运势
```bash
curl "http://localhost:5000/api/constellation/?sign=白羊座"
```

### 发送消息
```bash
curl -X POST http://localhost:5000/api/message/send \
  -H "Content-Type: application/json" \
  -d '{"message": "测试消息"}'
```

## 开发指南

### 添加新的API模块

1. 在 `api/` 目录下创建新的Python文件
2. 定义Flask蓝图和路由
3. 在 `api/__init__.py` 中导入并注册新的蓝图
4. 更新本文档

### 示例模块结构

```python
from flask import Blueprint, jsonify

# 创建蓝图
my_module_bp = Blueprint('my_module', __name__, url_prefix='/api/my-module')

@my_module_bp.route('/')
def my_endpoint():
    return jsonify({'message': 'Hello from my module'})

# 在 __init__.py 中注册
from .my_module import my_module_bp
api_bp.register_blueprint(my_module_bp)
```

## 部署说明

项目结构优化后，部署方式保持不变：

- **Docker部署**: 使用现有的Dockerfile和docker-compose.yml
- **本地部署**: 直接运行 `python wework_bot.py`
- **生产部署**: 使用 `api/index.py` 作为WSGI入口点

## 优势

1. **模块化**: 每个功能模块独立，便于维护和测试
2. **可扩展**: 新增功能只需添加新模块，不影响现有代码
3. **清晰结构**: API按功能分类，便于理解和使用
4. **向后兼容**: 保留旧路由，确保现有集成不受影响
5. **统一管理**: 通过蓝图统一管理所有API路由