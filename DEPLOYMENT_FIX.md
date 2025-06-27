# Vercel 部署修复说明

## 问题描述

在 Vercel 部署时遇到以下错误：
```
Traceback (most recent call last):
  File "/var/task/vc__handler__python.py", line 213, in <module>
    if not issubclass(base, BaseHTTPRequestHandler):
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: issubclass() arg 1 must be a class
```

## 修复内容

### 1. 修复 `api/index.py`
- 简化了 Vercel 入口点配置
- 添加了错误处理和 fallback 机制
- 确保正确导出 Flask 应用实例

### 2. 修复 `wework_bot.py`
- 添加了 Vercel 环境检测
- 在 Vercel 环境中禁用定时任务启动
- 改进了机器人实例的初始化逻辑
- 添加了错误处理和重复启动检查

### 3. 主要修改点

#### WeWorkBot 类改进
- 构造函数添加 `start_scheduler` 参数
- 添加 `scheduler_started` 状态跟踪
- 改进定时任务启动逻辑

#### 环境检测
```python
# 检测是否在Vercel环境中运行
is_vercel = os.getenv('VERCEL') == '1' or os.getenv('VERCEL_ENV') is not None
```

#### Flask 路由改进
- 所有路由都添加了机器人实例检查
- 使用 `get_bot_instance()` 函数进行延迟初始化

## 测试验证

运行 `test_vercel.py` 脚本可以验证修复效果：

```bash
python test_vercel.py
```

预期输出：
```
✅ 成功导入Flask应用
✅ Flask应用类型正确
✅ 健康检查接口正常
```

## 部署说明

1. 确保所有依赖都在 `requirements.txt` 中
2. 配置环境变量（可选）：
   - `WEBHOOK_URL`: 企业微信机器人 Webhook 地址
   - `ARK_API_KEY`: Volces Engine ARK API 密钥
   - `WEATHER_API_KEY`: 高德天气 API 密钥
   - `CITY`: 城市名称（默认：上海）

3. 在 Vercel 中部署时，定时任务会自动禁用
4. 可以通过 API 接口手动触发功能测试

## API 接口

- `GET /`: 健康检查
- `POST /send`: 手动发送消息
- `POST /send-daily`: 立即发送每日消息
- `GET /preview-daily`: 预览每日消息内容

## 注意事项

- 在 Vercel 环境中，定时任务功能被禁用（因为 Vercel 是无服务器环境）
- 如需定时功能，建议使用 Vercel Cron Jobs 或外部定时服务
- 所有功能都可以通过 API 接口手动触发