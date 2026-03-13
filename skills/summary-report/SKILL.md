---
name: summary-report
description: "从 Session 历史自动生成工作总结 PDF — 支持日报/周报/月报模板"
---

# 工作汇报生成技能

从会话历史自动提取信息，生成工作总结报告（支持日报、周报、月报），并导出为 PDF。

## 依赖

- **Python fpdf2** - PDF 生成（已安装）
- **sessions_list** - 获取会话历史
- **sessions_history** - 获取会话详情

## 核心能力

✅ Session 历史自动提取  
✅ 日报/周报/月报模板  
✅ PDF 精美输出  

## 使用方法

### 1. 获取会话历史

首先使用工具获取会话列表和历史：

```python
# 获取最近会话
sessions_list(limit=10)

# 获取会话详情
sessions_history(sessionKey="agent:main:xxx", limit=20)
```

### 2. 分析工作内容

从会话历史中提取：
- 完成的任务
- 解决的问题
- 学到的新技能
- 重要决策
- 待办事项

### 3. 生成报告

根据模板生成工作报告：

```python
from fpdf import FPDF

class WorkReportPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, '工作汇报', 0, 1, 'C')
        self.ln(5)
    
    def section_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 8, title, 0, 1, 'L', 1)
        self.ln(3)
    
    def content(self, text):
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 5, text)
        self.ln()

# 生成报告
pdf = WorkReportPDF()
pdf.add_page()
pdf.section_title("今日工作")
pdf.content("1. 完成了 xxx 功能\n2. 解决了 xxx 问题\n3. 学习了什么")
pdf.output("work_report.pdf")
```

### 4. 报告模板

#### 日报模板

```markdown
# 日报 - {日期}

## 今日完成
- [任务1]
- [任务2]

## 遇到的问题
- [问题1及解决方案]

## 明日计划
- [计划1]
- [计划2]
```

#### 周报模板

```markdown
# 周报 - {第N周} {日期范围}

## 本周总结
- 完成事项
- 解决问题
- 学习成长

## 数据统计
- 完成任务数
- 处理问题数

## 下周计划
- 重点任务
- 改进方向
```

#### 月报模板

```markdown
# 月报 - {月份}

## 本月工作概述
## 重点项目进展
## 团队协作
## 成果与收获
## 下月计划
```

## 用户对话示例

当用户说：
- "总结今天的工作"
- "生成本周工作报告"
- "帮我看看团队这周做了什么"
- "生成一份工作汇报 PDF"
- "做个周报"

执行相应的工作报告生成流程。

## 注意事项

1. 需要有会话历史数据才能生成报告
2. 可以指定时间范围（今日、本周、本月）
3. PDF 输出支持中文（需字体）
4. 可以自定义模板格式

## 输出文件

- `日报_YYYY-MM-DD.pdf`
- `周报_2026-WXX.pdf`
- `月报_YYYY-MM.pdf`
