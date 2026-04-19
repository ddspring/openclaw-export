---
name: ssh-exec
description: SSH 远程连接与命令执行技能。通过 Python paramiko 实现，支持密码/密钥认证、远程命令执行、文件上传下载。当用户说"SSH 连接"、"执行远程命令"、"连到服务器"、"run command on remote"、"SSH exec"时触发。技能会自动读取 ~/.ssh/config 或 scripts/ssh_hosts.json 中的主机配置。
---

# SSH Exec — 远程连接与命令执行

## 核心原则

- **Windows 上 SSH 密码认证无法交互完成**，因此使用 Python paramiko 库作为统一方案
- paramiko 支持密码和密钥认证，不依赖交互式终端
- 所有 SSH 操作通过 `scripts/ssh_exec.py` 执行，不要直接用 `ssh` 命令行

## 快速使用

### 方式一：指定连接参数（临时连接）

> ⚠️ **必须使用绝对路径或 `C:\Python313\python.exe`**，不要用 `python`/`py`（会被 uv run 等工具劫持）

```python
C:\Python313\python.exe scripts/ssh_exec.py --host 192.168.1.4 --port 22 --user root --pass "1234" --cmd "uname -a"
```

### 方式二：使用主机配置（复用配置）

```python
C:\Python313\python.exe scripts/ssh_exec.py --name tegra --cmd "uptime"
```

> 脚本自带环境检测：若发现当前 python 被劫持，会自动用 C:\Python313\python.exe 重启。

主机配置位于 `scripts/ssh_hosts.json`，示例：
```json
{
  "hosts": {
    "tegra": {
      "host": "192.168.1.4",
      "port": 22,
      "user": "root",
      "password": "1234"
    }
  }
}
```

## 高级用法

### 执行多条命令（分号分隔）
```python
python scripts/ssh_exec.py --name tegra --cmd "df -h && free -m"
```

### 上传文件
```python
python scripts/ssh_exec.py --name tegra --upload "local.txt:/remote/path/remote.txt"
```

### 下载文件
```python
python scripts/ssh_exec.py --name tegra --download "/remote/path/file.txt:local_copy.txt"
```

### 执行本地脚本到远程（上传+执行）
```python
python scripts/ssh_exec.py --name tegra --script "deploy.sh"
```

## 输出格式

脚本输出包含三部分：
- `=== STDOUT ===`：标准输出
- `=== STDERR ===`：错误输出（如有）
- `=== EXIT CODE ===`：退出码

## 错误处理

- 连接超时：检查网络和 SSH 服务是否运行
- 认证失败：检查用户名/密码是否正确
- 命令执行失败：查看 STDERR 输出

## 添加新主机

编辑 `scripts/ssh_hosts.json`，添加新的主机配置即可。新增主机后，所有团队成员均可使用该配置。
