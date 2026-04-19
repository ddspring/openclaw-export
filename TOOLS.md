# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## PDF生成工具

**重要：生成PDF必须使用 ReportLab 方案，禁止使用 fpdf2！**

### 标准PDF生成脚本
位置：`C:\Users\tsc\.qclaw\pdf_generator.py`

使用方式：
```bash
C:\Python313\python.exe "C:\Users\tsc\.qclaw\pdf_generator.py"
```

特点：
- 使用 ReportLab 库
- 支持中文字体（微软雅黑/宋体）
- 标题层级样式（区分大小标题）
- 表格美化（表头背景色、网格线）
- 段落两端对齐
- 合理间距控制

### fpdf2 方案（已废弃）
fpdf2 方案排版混乱，不适合中文文档，不要使用。

## 网络代理

- **Clash Verge** → 桌面上的代理软件，需要访问 Google、GitHub 等网站时打开，不需要时关闭
- **proxy-access skill** → `D:\QClawData\skills\proxy-access\SKILL.md`，封装了启动/关闭 Clash Verge 和访问外网的完整流程

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.
