"""
报告生成模块
生成Markdown格式的分析报告
"""
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class ReportGenerator:
    """分析报告生成器"""
    
    def __init__(self, report_path: str = './reports'):
        self.report_path = Path(report_path)
        self.report_path.mkdir(parents=True, exist_ok=True)
    
    def generate(self, results: Dict, log_files: List[str], total_lines: int) -> str:
        """生成分析报告"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.report_path / f"log_analysis_{timestamp}.md"
        
        content = self._build_report(results, log_files, total_lines)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(report_file)
    
    def _build_report(self, results: Dict, log_files: List[str], total_lines: int) -> str:
        """构建报告内容"""
        
        summary = results['summary']
        errors = results['errors']
        warnings = results['warnings']
        events = results.get('events', [])
        ai_analysis = results.get('ai_analysis', {})
        
        # 构建Markdown报告
        report = f"""# 日志智能分析报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 分析概要

| 指标 | 数值 |
|------|------|
| 日志文件数 | {len(log_files)} |
| 总日志行数 | {total_lines} |
| 错误数量 | {summary['error_count']} |
| 警告数量 | {summary['warning_count']} |

### 日志级别分布

"""
        
        # 添加级别分布
        for level, count in summary.get('level_distribution', {}).items():
            report += f"- **{level}**: {count}\n"
        
        report += f"""

---

## 🔴 错误日志分析

共发现 **{len(errors)}** 条错误日志

"""
        
        # 添加错误日志详情
        for i, error in enumerate(errors[:30], 1):
            level = error.get('level', 'ERROR')
            msg = error.get('message', '')
            ts = error.get('timestamp', '')
            
            report += f"### {i}. [{level}] {ts}\n\n"
            report += f"```\n{msg}\n```\n\n"
        
        if len(errors) > 30:
            report += f"\n*(还有 {len(errors) - 30} 条错误日志省略)*\n"
        
        report += f"""

---

## 🟡 警告日志分析

共发现 **{len(warnings)}** 条警告日志

"""
        
        # 添加警告日志详情
        for i, warning in enumerate(warnings[:20], 1):
            level = warning.get('level', 'WARN')
            msg = warning.get('message', '')
            ts = warning.get('timestamp', '')
            
            report += f"### {i}. [{level}] {ts}\n\n"
            report += f"```\n{msg}\n```\n\n"
        
        if len(warnings) > 20:
            report += f"\n*(还有 {len(warnings) - 20} 条警告日志省略)*\n"
        
        # 关键事件分析
        if events:
            # 按事件类型分组统计
            event_types = {}
            for e in events:
                evt = e.get('event', 'UNKNOWN')
                event_types[evt] = event_types.get(evt, 0) + 1
            
            report += f"""

---

## 🟢 关键事件分析

共发现 **{len(events)}** 条关键事件

### 事件类型分布

"""
            for evt, count in sorted(event_types.items(), key=lambda x: x[1], reverse=True):
                report += f"- **{evt}**: {count}\n"
            
            report += f"""

### 关键事件示例（显示前20条）

"""
            for i, event in enumerate(events[:20], 1):
                evt = event.get('event', '')
                msg = event.get('message', '')[:150]
                ts = event.get('timestamp', '')
                device = event.get('device', '')
                
                report += f"**{i}. [{evt}]** {ts} {device}\n"
                report += f"```\n{msg}\n```\n\n"
        
        report += """

---

## 🤖 AI智能分析

"""
        
        if ai_analysis.get('status') == 'success':
            report += ai_analysis.get('analysis', '无分析结果')
        else:
            report += f"❌ {ai_analysis.get('analysis', '分析失败')}"
        
        report += f"""

---

## 📁 分析的日志文件

"""
        
        for f in log_files:
            report += f"- {f}\n"
        
        report += """

---

*报告由日志智能分析系统自动生成*
"""
        
        return report
