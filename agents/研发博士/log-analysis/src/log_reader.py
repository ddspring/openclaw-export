"""
日志读取模块
支持文件格式日志的读取
"""
import re
from pathlib import Path
from typing import List, Dict, Optional


class LogReader:
    """日志文件读取器"""
    
    # 常见日志格式正则
    LOG_PATTERNS = [
        # 标准格式: 2024-01-01 10:00:00 [ERROR] message
        r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s*\[(\w+)\]\s*(.*)',
        # 简略格式: 2024-01-01 10:00:00 ERROR message
        r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+(\w+)\s+(.*)',
        # 时间戳格式: 1704067200 ERROR message
        r'(\d{10})\s+(\w+)\s+(.*)',
        # 交换机格式: 2025/12/16 15:18:45-595 switch %01-5-DEFAULT-INFO(l):[HEARTBEAT] message
        r'(\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}:\d{2}-\d{3})\s+(\S+)\s+(\S+)-(\d+)-(\S+)-(\w+)\((\w+)\):\[(\w+)\]\s*(.*)',
    ]
    
    def __init__(self, encoding: str = 'utf-8', max_lines: int = 100000):
        self.encoding = encoding
        self.max_lines = max_lines
        self.patterns = [re.compile(p) for p in self.LOG_PATTERNS]
    
    def read_file(self, file_path: str) -> List[Dict]:
        """读取日志文件"""
        logs = []
        
        try:
            with open(file_path, 'r', encoding=self.encoding, errors='ignore') as f:
                for i, line in enumerate(f):
                    if i >= self.max_lines:
                        break
                    
                    line = line.strip()
                    if not line:
                        continue
                    
                    parsed = self._parse_line(line)
                    logs.append(parsed)
                    
        except FileNotFoundError:
            print(f"   ❌ 文件未找到: {file_path}")
        except Exception as e:
            print(f"   ❌ 读取错误: {e}")
        
        return logs
    
    def _parse_line(self, line: str) -> Dict:
        """解析单行日志"""
        for pattern in self.patterns:
            match = pattern.match(line)
            if match:
                groups = match.groups()
                # 交换机格式: 2025/12/16 15:18:45-595 switch %01-5-DEFAULT-INFO(l):[HEARTBEAT] message
                if len(groups) == 10:
                    # 提取事件类型 - 方括号中的内容
                    event_match = groups[8] if groups[8] else groups[7]  # [HEARTBEAT] 或 [devMac]
                    if event_match and event_match.startswith('['):
                        event_type = event_match[1:-1]  # 去掉[]
                    else:
                        event_type = event_match
                    
                    return {
                        'timestamp': groups[0],
                        'device': groups[1],
                        'module': groups[2],
                        'level': groups[5],  # INFO
                        'event': event_type,  # HEARTBEAT, devMac
                        'message': groups[9],
                        'raw': line
                    }
                elif len(groups) == 3:
                    return {
                        'timestamp': groups[0],
                        'level': groups[1],
                        'message': groups[2],
                        'raw': line
                    }
        
        # 无法解析，尝试提取方括号中的内容作为事件
        import re
        bracket_match = re.search(r'\[(\w+)\]', line)
        event_type = bracket_match.group(1) if bracket_match else None
        
        # 返回原始格式
        return {
            'timestamp': None,
            'level': 'INFO',
            'event': event_type,
            'message': line,
            'raw': line
        }
    
    def scan_directory(self, log_dir: str, extension: str = '.log') -> List[Path]:
        """扫描目录下的所有日志文件"""
        log_path = Path(log_dir)
        if not log_path.exists():
            return []
        
        return list(log_path.glob(f"*{extension}")) + \
               list(log_path.glob(f"*{extension}.txt"))
