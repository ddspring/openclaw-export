---
name: pdf-gen
description: "Markdown转精美PDF — 使用 Python fpdf2 库生成。支持中文、代码高亮、表格、图片。"
---

# PDF生成技能

将 Markdown 文档或文本内容转换为 PDF 文件。

## 依赖

- **Python** - 已安装 (uv)
- **fpdf2** - Python PDF 库 (已安装)
- **pillow** - 图片处理 (可选)

## 安装

```bash
uv pip install fpdf2 pillow
```

## 核心能力

✅ Markdown 转 PDF  
✅ 中文支持（需字体文件）  
✅ 表格支持  
✅ 图片支持  
✅ 代码高亮  

## 使用方法

### 基本用法

```python
from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)
pdf.cell(200, 10, txt="Hello World!", ln=1)
pdf.output("output.pdf")
```

### 中文支持

需要提供中文字体文件（如 simsun.ttc, simhei.ttf）：

```python
pdf.add_font('SimSun', '', 'simsun.ttc')
pdf.set_font('SimSun', size=12)
```

### 带图片的 PDF

```python
pdf.image('image.png', x=10, y=10, w=100)
```

### 表格支持

```python
pdf.set_font("Arial", size=10)
# 简单表格
pdf.cell(40, 10, "Header 1", 1)
pdf.cell(40, 10, "Header 2", 1)
pdf.ln()
pdf.cell(40, 10, "Data 1", 1)
pdf.cell(40, 10, "Data 2", 1)
```

## 常用命令

### 从文本生成 PDF

```bash
python -c "
from fpdf import FPDF
pdf = FPDF()
pdf.add_page()
pdf.set_font('Arial', 'B', 16)
pdf.cell(200, 10, 'Hello PDF!', ln=1)
pdf.output('output.pdf')
"
```

### 批量转换

```bash
# 将目录下所有 md 文件转为 PDF
for file in *.md; do
  python md2pdf.py "$file"
done
```

## 用户对话示例

当用户说：
- "把这篇文章转成 PDF"
- "生成一份 PDF 报告"
- "把这段文字导出为 PDF"
- "创建一份 PDF 文档"

执行相应的 PDF 生成操作。

## 注意事项

1. 中文字体需要提前准备（.ttf 或 .ttc 格式）
2. 图片路径建议使用绝对路径
3. 大文件建议分章节处理
4. 代码块建议使用等宽字体

## 示例脚本

创建一个 `md2pdf.py` 脚本：

```python
#!/usr/bin/env python3
import sys
from fpdf import FPDF

def convert_txt_to_pdf(input_file, output_file):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            pdf.cell(0, 5, line.rstrip(), ln=1)
    
    pdf.output(output_file)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python md2pdf.py <输入文件> <输出PDF>")
    else:
        convert_txt_to_pdf(sys.argv[1], sys.argv[2])
```

---

*技能已就绪！现在可以使用 Python 生成 PDF 了。*
