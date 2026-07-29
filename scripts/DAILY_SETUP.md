# 每日自动化流程设置指南

## 概述

设置完成后，系统每天18:00自动：
1. 采集前一天arXiv量化/压缩论文
2. 筛选相关论文并下载PDF
3. 生成深度技术分析
4. 生成独立PyTorch代码（针对<=4bit/<=8bit论文）
5. 推送到GitHub分支 `daily/YYYY-MM-DD`

---

## 安装步骤

### 1. 安装依赖

```bash
cd reading_machine
pip install requests pyyaml feedparser
```

### 2. 配置定时任务（macOS）

```bash
# 复制plist到LaunchAgents
cp scripts/ai.openclaw.reading-machine.plist ~/Library/LaunchAgents/

# 加载定时任务
launchctl load ~/Library/LaunchAgents/ai.openclaw.reading-machine.plist

# 验证已加载
launchctl list | grep ai.openclaw.reading-machine

# 立即测试运行（可选）
launchctl start ai.openclaw.reading-machine
```

### 3. 配置GitHub推送

确保本地Git配置了正确的远程仓库和认证：

```bash
# 验证远程地址
git remote -v

# 如果使用HTTPS+Token，确保Token有效
# 如果使用SSH，确保密钥已配置
```

### 4. 配置关键词（可选）

编辑 `scripts/daily_config.yaml` 调整采集关键词和筛选条件：

```yaml
collection:
  keywords:
    - "quantization"
    - "model compression"
    # ... 添加更多关键词
```

---

## 定时任务管理

```bash
# 查看状态
launchctl list | grep reading-machine

# 手动触发
launchctl start ai.openclaw.reading-machine

# 停止定时任务
launchctl unload ~/Library/LaunchAgents/ai.openclaw.reading-machine.plist

# 重新加载（修改配置后）
launchctl unload ~/Library/LaunchAgents/ai.openclaw.reading-machine.plist
launchctl load ~/Library/LaunchAgents/ai.openclaw.reading-machine.plist
```

---

## 日志查看

```bash
# 查看实时日志
tail -f logs/launchd.stdout.log

# 查看错误日志
tail -f logs/launchd.stderr.log

# 查看历史日志
ls -lt logs/
cat logs/daily_2026-07-29_180001.log
```

---

## 分支命名规范

每天自动创建的分支：
- 格式: `daily/YYYY-MM-DD`
- 示例: `daily/2026-07-29`

提交信息格式：
```
daily: 2026-07-29 arxiv quantization analysis

- Auto-collected papers for 2026-07-29
- Filtered by quantization/compression keywords
- Generated technical analyses
- Created standalone PyTorch demos for <=4bit/<=8bit papers
```

---

## 自动化范围

### 完全自动化的步骤 ✅
1. arXiv API采集
2. 关键词筛选
3. PDF下载
4. 结构化索引更新
5. Git分支创建和推送

### 需要AI辅助的步骤 🤖
6. **深度技术分析** — 当前为模板占位符
   - 方案A: 集成OpenAI API自动分析
   - 方案B: 使用OpenClaw session spawn触发AI分析
   - 方案C: 手动审查和补充

7. **PyTorch代码生成** — 当前为模板占位符
   - 需要基于论文内容手动实现或AI生成

### 推荐工作流
1. 每天18:00自动执行采集和归档
2. 次日早晨审查分支内容
3. 使用AI工具补充深度分析和代码
4. 提交更新并合并到main

---

## 故障排查

### 问题1: arXiv API返回空结果
```bash
# 检查网络连接
curl -I http://export.arxiv.org/api/query

# 检查日期格式
python3 -c "from datetime import datetime, timedelta; print((datetime.now()-timedelta(days=1)).strftime('%Y-%m-%d'))"
```

### 问题2: Git推送失败
```bash
# 检查认证
git push origin daily/2026-07-29 --dry-run

# 更新Token（如使用HTTPS）
git remote set-url origin https://TOKEN@github.com/njulpc/reading_machine.git
```

### 问题3: PDF下载失败
```bash
# 检查磁盘空间
df -h

# 手动测试下载
curl -L -o test.pdf https://arxiv.org/pdf/2607.25870.pdf
```

---

## 扩展配置

### 添加Slack/Discord通知

在 `daily_run.sh` 末尾添加：
```bash
# Slack通知
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Daily ArXiv pipeline complete: '"${BRANCH_NAME}"'"}' \
  YOUR_SLACK_WEBHOOK_URL

# Discord通知
curl -X POST -H 'Content-type: application/json' \
  --data '{"content":"Daily ArXiv pipeline complete: '"${BRANCH_NAME}"'"}' \
  YOUR_DISCORD_WEBHOOK_URL
```

### 调整执行时间

编辑 `ai.openclaw.reading-machine.plist`：
```xml
<key>StartCalendarInterval</key>
<dict>
    <key>Hour</key>
    <integer>9</integer>    <!-- 改为早上9点 -->
    <key>Minute</key>
    <integer>0</integer>
</dict>
```

然后重新加载：
```bash
launchctl unload ~/Library/LaunchAgents/ai.openclaw.reading-machine.plist
launchctl load ~/Library/LaunchAgents/ai.openclaw.reading-machine.plist
```

---

*配置时间: 2026-07-29*
