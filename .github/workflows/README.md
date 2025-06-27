# GitHub Actions 定时推送配置说明

## 📋 功能说明

这个 GitHub Actions 工作流会自动在每个工作日上午 9:00（北京时间）触发企业微信机器人发送日报消息。

## ⚙️ 配置步骤

### 1. 设置 GitHub Secrets

在你的 GitHub 仓库中设置以下 Secret：

1. 进入 GitHub 仓库页面
2. 点击 `Settings` → `Secrets and variables` → `Actions`
3. 点击 `New repository secret`
4. 添加以下 Secret：

| Secret 名称 | 值 | 说明 |
|------------|----|---------|
| `VERCEL_APP_URL` | `https://your-app.vercel.app` | 你的 Vercel 应用 URL |

### 2. 启用 GitHub Actions

1. 确保你的仓库启用了 GitHub Actions
2. 推送代码到 GitHub 后，Actions 会自动运行

### 3. 验证配置

#### 手动触发测试
1. 进入 GitHub 仓库的 `Actions` 页面
2. 选择 `Daily WeWork Message` 工作流
3. 点击 `Run workflow` 按钮手动触发
4. 查看执行日志确认是否成功

#### 查看定时执行
- 工作流会在每个工作日上午 9:00（北京时间）自动执行
- 可以在 `Actions` 页面查看执行历史和日志

## 🕐 时间设置说明

当前配置：
- **Cron 表达式**: `0 1 * * 1-5`
- **执行时间**: 每周一到周五的 01:00 UTC
- **北京时间**: 上午 9:00

### 修改执行时间

如果需要修改执行时间，编辑 `daily-message.yml` 文件中的 cron 表达式：

```yaml
schedule:
  - cron: '分钟 小时 日 月 星期'  # UTC 时间
```

**常用时间对照表**（北京时间 → UTC 时间）：
- 上午 8:00 → `0 0 * * 1-5`
- 上午 9:00 → `0 1 * * 1-5`（当前设置）
- 上午 10:00 → `0 2 * * 1-5`
- 下午 6:00 → `0 10 * * 1-5`

## 🔍 故障排除

### 常见问题

1. **工作流执行失败**
   - 检查 `VERCEL_APP_URL` Secret 是否正确设置
   - 确认 Vercel 应用是否正常运行
   - 查看 Actions 日志获取详细错误信息

2. **消息发送失败**
   - 检查企业微信机器人配置
   - 确认 Vercel 应用的环境变量设置
   - 查看 Vercel 应用日志

3. **定时任务不执行**
   - GitHub Actions 可能有延迟（通常 5-15 分钟）
   - 确认仓库是否为公开仓库或有 GitHub Actions 权限

### 调试方法

1. **手动触发测试**：使用 `workflow_dispatch` 手动运行
2. **查看日志**：在 Actions 页面查看详细执行日志
3. **本地测试**：直接访问 Vercel 应用的 `/send-daily` 接口

## 📝 注意事项

- GitHub Actions 对于公开仓库是免费的
- 私有仓库有每月免费额度限制
- 定时任务可能有 5-15 分钟的延迟
- 如果仓库长期不活跃，GitHub 可能会禁用定时任务

## 🚀 扩展功能

可以根据需要添加更多功能：

1. **多时间点推送**：添加更多 cron 表达式
2. **失败通知**：集成邮件或其他通知方式
3. **条件执行**：根据日期或其他条件决定是否执行
4. **批量操作**：同时触发多个接口