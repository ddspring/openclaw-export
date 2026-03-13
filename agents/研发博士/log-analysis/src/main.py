"""
日志智能分析系统主程序
"""
import os
import sys
import yaml
from pathlib import Path
from log_reader import LogReader
from analyzer import LogAnalyzer
from reporter import ReportGenerator

# 设置UTF-8输出
sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def load_config(config_path: str = "config/config.yaml") -> dict:
    """加载配置文件"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def main():
    # 加载配置
    config = load_config()
    
    print("=" * 50)
    print("日志智能分析系统")
    print("=" * 50)
    
    # 初始化日志读取器
    log_config = config['log']
    log_path = log_config['path']
    
    print(f"\n[日志目录] {log_path}")
    print(f"[日志格式] {log_config['format']}")
    
    # 检查日志目录
    if not os.path.exists(log_path):
        print(f"\n[!] 警告: 日志目录不存在 - {log_path}")
        print("   将在运行时创建样例日志...")
        # 创建日志目录
        os.makedirs(log_path, exist_ok=True)
    
    # 初始化分析器
    llm_config = config['llm']
    analyzer = LogAnalyzer(
        provider=llm_config['provider'],
        api_key=llm_config['api_key'],
        base_url=llm_config['base_url'],
        model=llm_config.get('model', 'MiniMax-M2.5')
    )
    
    # 初始化报告生成器
    report_config = config.get('output', {})
    reporter = ReportGenerator(
        report_path=report_config.get('report_path', './reports')
    )
    
    # 扫描日志文件
    # 支持有扩展名(.log)和无扩展名的文件，也支持子目录
    log_files = list(Path(log_path).glob(f"*{log_config.get('extension', '.log')}"))
    if not log_files:
        # 递归扫描所有.log文件
        log_files = list(Path(log_path).rglob("*.log"))
    print(f"\n[*] 发现 {len(log_files)} 个日志文件:")
    
    for log_file in log_files:
        print(f"   - {log_file.name}")
    
    if not log_files:
        print("\n[!] 未找到日志文件")
        return
    
    # 读取日志
    reader = LogReader(
        encoding=log_config.get('encoding', 'utf-8'),
        max_lines=config.get('analysis', {}).get('max_lines', 100000)
    )
    
    all_logs = []
    for log_file in log_files:
        print(f"\n[读取] {log_file.name}")
        logs = reader.read_file(str(log_file))
        all_logs.extend(logs)
        print(f"   -> 读取 {len(logs)} 行日志")
    
    # 分析日志
    print("\n[AI分析] 开始分析...")
    analysis_config = config.get('analysis', {})
    results = analyzer.analyze(
        logs=all_logs,
        error_keywords=analysis_config.get('error_keywords', ['ERROR', 'FATAL']),
        warning_keywords=analysis_config.get('warning_keywords', ['WARNING', 'WARN']),
        event_keywords=analysis_config.get('event_keywords', ['HEARTBEAT', 'MAC', 'OSPF', 'TTDP'])
    )
    
    # 生成报告
    print("\n[报告] 生成分析报告...")
    report_path = reporter.generate(
        results=results,
        log_files=[f.name for f in log_files],
        total_lines=len(all_logs)
    )
    
    print(f"\n[完成] 分析完成!")
    print(f"[报告] {report_path}")


if __name__ == "__main__":
    main()
