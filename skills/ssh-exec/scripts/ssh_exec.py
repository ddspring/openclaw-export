#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSH Remote Execution Script
使用 Python paramiko 实现，支持密码/密钥认证、远程命令执行、文件上传下载

注意：使用 C:\\Python313\\python.exe 绕过 uv run 劫持，确保依赖可用。

用法：
  python ssh_exec.py --host <IP> --user <user> --pass <pass> --cmd "<command>"
  python ssh_exec.py --name <host_alias> --cmd "<command>"
  python ssh_exec.py --name <host_alias> --upload <local:remote>
  python ssh_exec.py --name <host_alias> --download <remote:local>
"""

import sys
import os

# 强制使用系统 Python，绕过 uv run / conda 等环境劫持
_python_exe = r"C:\Python313\python.exe"
if getattr(sys, 'frozen', False):
    pass  # PyInstaller 打包后维持 sys.executable
elif os.path.basename(sys.executable).lower() not in ('python.exe', 'python'):
    # 当前 python 被劫持（如 uv run），用系统 Python 重新执行自身
    os.execv(_python_exe, [_python_exe, __file__] + sys.argv[1:])

import json
import argparse

# paramiko 已在 C:\Python313 中，随系统 Python 一起安装
try:
    import paramiko
except ImportError:
    import subprocess
    print("[INFO] paramiko 未安装，正在安装...", file=sys.stderr)
    subprocess.check_call([_python_exe, "-m", "pip", "install", "-q", "paramiko"])
    import paramiko


def load_hosts_config():
    """加载主机配置文件，搜索路径：当前目录、scripts目录、~/.ssh/"""
    search_dirs = [
        os.path.dirname(os.path.abspath(__file__)),
        os.path.expanduser("~/.ssh"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"),
    ]
    # 也搜索 workspace 根目录
    workspace = os.environ.get("WORKSPACE_MAIN", os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    search_dirs.insert(0, workspace)

    for search_dir in search_dirs:
        config_path = os.path.join(search_dir, "ssh_hosts.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("hosts", {})
            except Exception as e:
                print(f"[WARN] 加载 {config_path} 失败: {e}", file=sys.stderr)
    return {}


def connect_ssh(host, port, username, password=None, key_file=None, timeout=15):
    """建立 SSH 连接"""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(
            hostname=host,
            port=port,
            username=username,
            password=password,
            key_filename=key_file,
            timeout=timeout,
            allow_agent=False,
            look_for_keys=False,
            banner_timeout=15,
        )
        return client
    except Exception as e:
        print(f"[ERROR] SSH 连接失败: {type(e).__name__}: {e}", file=sys.stderr)
        return None


def exec_command(client, command):
    """执行远程命令并返回结果"""
    sys.stdout.reconfigure(encoding="utf-8", write_through=True)

    stdin, stdout, stderr = client.exec_command(command, get_pty=False)
    exit_code = stdout.channel.recv_exit_status()

    out_data = stdout.read().decode("utf-8", errors="replace")
    err_data = stderr.read().decode("utf-8", errors="replace")

    if out_data:
        print("=== STDOUT ===")
        print(out_data, end="")
    if err_data:
        print("=== STDERR ===")
        print(err_data, end="")
    print(f"=== EXIT CODE: {exit_code} ===")

    return exit_code


def upload_file(client, local_path, remote_path):
    """上传文件到远程服务器"""
    try:
        sftp = client.open_sftp()
        sftp.put(local_path, remote_path)
        sftp.close()
        print(f"[OK] 上传成功: {local_path} -> {remote_path}")
        return True
    except Exception as e:
        print(f"[ERROR] 上传失败: {type(e).__name__}: {e}", file=sys.stderr)
        return False


def download_file(client, remote_path, local_path):
    """从远程服务器下载文件"""
    try:
        sftp = client.open_sftp()
        sftp.get(remote_path, local_path)
        sftp.close()
        print(f"[OK] 下载成功: {remote_path} -> {local_path}")
        return True
    except Exception as e:
        print(f"[ERROR] 下载失败: {type(e).__name__}: {e}", file=sys.stderr)
        return False


def run_local_script(client, local_script_path):
    """将本地脚本上传到远程并执行"""
    if not os.path.exists(local_script_path):
        print(f"[ERROR] 本地脚本不存在: {local_script_path}", file=sys.stderr)
        return 1

    script_name = os.path.basename(local_script_path)
    remote_path = f"/tmp/{script_name}"

    if not upload_file(client, local_script_path, remote_path):
        return 1

    # 自动添加执行权限并运行
    exec_cmd(client, f"chmod +x {remote_path} && {remote_path}")
    return 0


def main():
    parser = argparse.ArgumentParser(description="SSH Remote Execution Tool")
    parser.add_argument("--host", help="远程主机 IP 地址")
    parser.add_argument("--port", type=int, default=22, help="SSH 端口，默认 22")
    parser.add_argument("--user", help="用户名")
    parser.add_argument("--pass", dest="password", help="密码")
    parser.add_argument("--key", dest="key_file", help="私钥文件路径")
    parser.add_argument("--name", help="主机别名（从 ssh_hosts.json 读取）")
    parser.add_argument("--cmd", help="要执行的远程命令")
    parser.add_argument("--upload", help="上传文件，格式 local:remote")
    parser.add_argument("--download", help="下载文件，格式 remote:local")
    parser.add_argument("--script", help="本地脚本路径（上传到远程并执行）")
    parser.add_argument("--timeout", type=int, default=15, help="连接超时（秒），默认 15")

    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    # 解析主机配置
    host, port, username, password, key_file = args.host, args.port, args.user, args.password, args.key_file

    if args.name:
        hosts = load_hosts_config()
        if args.name not in hosts:
            print(f"[ERROR] 未找到主机配置: {args.name}", file=sys.stderr)
            print(f"可用主机: {', '.join(hosts.keys())}", file=sys.stderr)
            sys.exit(1)
        cfg = hosts[args.name]
        host = cfg.get("host", host)
        port = cfg.get("port", port)
        username = cfg.get("user", cfg.get("username", username))
        password = cfg.get("password", password)
        key_file = cfg.get("key_file", key_file)

    if not host or not username:
        parser.print_help()
        sys.exit(1)

    # 建立连接
    print(f"[INFO] 连接 {host}:{port} 用户 {username} ...", file=sys.stderr)
    client = connect_ssh(host, port, username, password, key_file, args.timeout)
    if not client:
        sys.exit(1)

    print("[OK] 连接成功", file=sys.stderr)

    try:
        # 执行操作
        if args.cmd:
            exit_code = exec_command(client, args.cmd)
            sys.exit(exit_code)
        elif args.upload:
            local, remote = args.upload.split(":", 1)
            success = upload_file(client, local.strip(), remote.strip())
            sys.exit(0 if success else 1)
        elif args.download:
            remote, local = args.download.split(":", 1)
            success = download_file(client, remote.strip(), local.strip())
            sys.exit(0 if success else 1)
        elif args.script:
            exit_code = run_local_script(client, args.script)
            sys.exit(exit_code)
        else:
            print("[INFO] 无指定操作，保持连接打开 5 秒后退出", file=sys.stderr)
            import time
            time.sleep(5)
    finally:
        client.close()


if __name__ == "__main__":
    main()
