"""
日志分析模块
使用LLM进行智能日志分析
"""
import json
from typing import List, Dict, Optional
import requests


class LogAnalyzer:
    """日志智能分析器"""
    
    def __init__(self, provider: str, api_key: str, base_url: str, model: str = "MiniMax-M2.5"):
        self.provider = provider
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        
    def analyze(self, logs: List[Dict], error_keywords: List[str], warning_keywords: List[str], event_keywords: List[str] = None) -> Dict:
        """分析日志"""
        
        # 1. 统计日志概要
        summary = self._get_summary(logs, error_keywords, warning_keywords)
        
        # 2. 提取错误和警告日志
        errors = [log for log in logs if self._match_level(log, error_keywords)]
        warnings = [log for log in logs if self._match_level(log, warning_keywords)]
        
        # 3. 提取关键事件（用于分析INFO中的重要事件）
        events = []
        if event_keywords:
            events = [log for log in logs if self._match_event(log, event_keywords)]
        
        # 4. 准备LLM分析
        sample_errors = errors[:20] if errors else []
        sample_warnings = warnings[:20] if warnings else []
        sample_events = events[:20] if events else []
        
        # 5. 调用LLM进行深度分析
        ai_analysis = self._call_llm(sample_errors, sample_warnings, sample_events)
        
        return {
            'summary': summary,
            'errors': errors,
            'warnings': warnings,
            'events': events,
            'ai_analysis': ai_analysis,
            'total_logs': len(logs)
        }
    
    def _get_summary(self, logs: List[Dict], error_keywords: List[str], warning_keywords: List[str]) -> Dict:
        """获取日志概要统计"""
        level_count = {}
        
        for log in logs:
            level = log.get('level', 'UNKNOWN')
            level_count[level] = level_count.get(level, 0) + 1
        
        return {
            'total': len(logs),
            'error_count': sum(1 for log in logs if self._match_level(log, error_keywords)),
            'warning_count': sum(1 for log in logs if self._match_level(log, warning_keywords)),
            'level_distribution': level_count
        }
    
    def _match_level(self, log: Dict, keywords: List[str]) -> bool:
        """检查日志级别是否匹配关键字"""
        level = log.get('level', '').upper()
        return any(kw.upper() in level for kw in keywords)
    
    def _match_event(self, log: Dict, keywords: List[str]) -> bool:
        """检查日志事件是否匹配关键字"""
        event = log.get('event') or ''
        message = log.get('message', '').upper()
        event_upper = event.upper() if event else ''
        return any(kw.upper() in event_upper or kw.upper() in message for kw in keywords)
    
    def _call_llm(self, errors: List[Dict], warnings: List[Dict], events: List[Dict]) -> Dict:
        """调用LLM进行智能分析"""
        
        # 构建提示词
        prompt = self._build_prompt(errors, warnings, events)
        
        # 调用miniMax API
        try:
            response = self._call_minimax(prompt)
            return {
                'status': 'success',
                'analysis': response
            }
        except Exception as e:
            return {
                'status': 'error',
                'analysis': f"LLM调用失败: {str(e)}"
            }
    
    def _build_prompt(self, errors: List[Dict], warnings: List[Dict], events: List[Dict]) -> str:
        """构建分析提示词"""
        
        error_msgs = '\n'.join([f"- [{e.get('level')}] {e['message'][:100]}" for e in errors[:10]])
        warning_msgs = '\n'.join([f"- [{w.get('level')}] {w.get('event','')}: {w['message'][:100]}" for w in warnings[:10]])
        event_msgs = '\n'.join([f"- [{e.get('event','')}] {e['message'][:100]}" for e in events[:15]])
        
        prompt = f"""请分析以下ETBN交换机日志中的关键信息：

## 错误日志 ({len(errors)}条):
{error_msgs or '无'}

## 警告日志 ({len(warnings)}条):
{warning_msgs or '无'}

## 关键事件 ({len(events)}条，显示前15条):
{event_msgs or '无'}

请分析:
1. 网络设备运行状态是否正常
2. 是否有异常事件（如CPU告警、端口变化、MAC变化等）
3. 关键事件的时间分布和模式
4. 建议的关注点

请用中文回复，分析要简洁明了。"""
        
        return prompt
    
    def _call_minimax(self, prompt: str) -> str:
        """调用miniMax API"""
        
        url = f"{self.base_url}/text/chatcompletion_v2"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个专业的日志分析专家，擅长分析系统日志、错误日志，定位问题原因并给出解决方案。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            raise Exception(f"API调用失败: {response.status_code} - {response.text}")
