# OpenClaw 导出配置包

> 一键导入你的 OpenClaw 配置、技能和 Agent

## 📦 包含内容

```
openclaw-export/
├── README.md              # 本文件
├── config-template.toml   # 配置模板
├── skills/                # 技能包
│   ├── github/
│   ├── himalaya/
│   ├── inner-life-core/
│   ├── pdf-gen/
│   ├── playwright-scraper-skill/
│   └── summary-report/
└── agents/                # Agent 配置
    ├── 产品经理/
    ├── 文案写手/
    ├── 运营专员/
    ├── 研究分析师/
    └── 总结助手/
```

## 🚀 快速导入

### 1. 导入技能

```bash
# 方式一：复制到 skills 目录
cp -r skills/* ~/.openclaw/skills/

# 方式二：使用 OpenClaw CLI
openclaw skills install ./skills/github
```

### 2. 导入 Agent

将 `agents/` 目录下的文件夹复制到你的 Agent 配置目录。

### 3. 配置 OpenClaw

复制 `config-template.toml` 为 `config.toml`，修改其中的：
- 邮箱账号密码
- API Keys（智谱、MiniMax 等）
- 频道配置（飞书、Telegram 等）

## 📚 技能说明

| 技能 | 功能 |
|------|------|
| github | GitHub 操作 - Issues、PR、Actions |
| himalaya | 邮件管理 - IMAP/SMTP |
| inner-life-core | 情感记忆系统 |
| pdf-gen | Markdown 转 PDF |
| playwright-scraper-skill | 网页爬虫 |
| summary-report | 工作报告生成 |

## 🔧 自行部署

参考官方文档：https://docs.openclaw.ai

## 📄 许可证

MIT
