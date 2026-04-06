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
    ├── 产品军师/
    ├── 参谋官/
    ├── 政经助理/
    ├── 研发博士/
    ├── 管家/
    └── 质量总监/
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

## 🤖 数字团队成员

项目预配置了 6 位数字团队成员：

| 成员 | ID | 擅长领域 |
|------|----|----------|
| 产品军师 | chanpin-junshi | 产品规划、需求分析 |
| 参谋官 | canmou-guan | PPT、演示、策略汇报 |
| 政经助理 | zhengjing-zhuli | 政经资讯、新闻、行业趋势 |
| 研发博士 | yanfa-boshi | 技术研究、代码、架构 |
| 管家 | guanjia | 日程、提醒、整理、进度跟踪 |
| 质量总监 | zhiliang-zongjian | 质量审查、评分、触发返工 |

**质量总监工作流**：
- 自动审查研发博士、产品军师、参谋官、管家的输出
- 评分低于 80 分则触发返工，最多返工 3 次
- 3 次返工后仍不通过则上报人工处理

## 🔧 自行部署

参考官方文档：https://docs.openclaw.ai

## 📄 许可证

MIT