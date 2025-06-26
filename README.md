# 企业微信群机器人 - Volces Engine ARK版

基于Flask的企业微信群机器人，集成Volces Engine ARK API，支持智能对话和自动回复功能。

## 功能特性

- 🤖 **智能对话**: 集成Volces Engi ne ARK API，提供智能AI回复
- 📱 **企业微信集成**: 支持企业微信群机器人webhook
- 🔄 **自动回复**: 当AI API不可用时，自动切换到本地辩论逻辑
- 🚀 **云端部署**: 支持Vercel等Serverless平台部署
- 🛡️ **安全可靠**: 支持环境变量配置，保护API密钥安全

## 快速开始

### 1. 环境配置

在Vercel中配置以下环境变量：

```bash
# 企业微信群机器人Webhook URL
WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=your_webhook_key

# Volces Engine ARK API配置
ARK_API_KEY=your_ark_api_key_here
ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
```

### 2. 部署到Vercel

1. Fork此仓库到你的GitHub账号
2. 在Vercel中导入项目
3. 配置上述环境变量
4. 部署完成后获取域名，配置企业微信webhook

## API接口

### 健康检查
```
GET /
```

### Webhook接收
```
POST /webhook
```
接收企业微信群消息并自动回复。

### 手动发送消息
```
POST /send
Content-Type: application/json

{
  "content": "要发送的消息内容"
}
```

### 聊天测试
```
POST /chat
Content-Type: application/json

{
  "message": "你好"
}
```

## 技术栈

- **后端框架**: Flask
- **AI服务**: Volces Engine ARK API
- **部署平台**: Vercel (Serverless)
- **依赖管理**: pip + requirements.txt

## 许可证

MIT License