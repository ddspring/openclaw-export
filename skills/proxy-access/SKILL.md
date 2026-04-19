# Proxy Access Skill

通过 Clash Verge 代理访问外网（Google、GitHub、Twitter 等）。

## 触发条件

当需要访问以下网站时使用此 skill：
- Google、YouTube、Twitter/X、Facebook、Instagram
- GitHub Gist、GitHub Raw 文件
- 其他被墙的外网资源

## 工作流程

### 1. 启动代理

```powershell
# 检查 Clash Verge 是否运行
$process = Get-Process -Name "clash-verge" -ErrorAction SilentlyContinue
if (-not $process) {
    # 启动 Clash Verge（桌面快捷方式）
    Start-Process "C:\Users\tsc\Desktop\Clash Verge.lnk"
    Start-Sleep -Seconds 5  # 等待代理生效
}
```

### 2. 访问外网

代理启动后，可使用以下方式访问：

**方式 A：online-search skill（推荐）**
- 使用腾讯元宝搜索，自动获取外网内容摘要
- 适合：搜索信息、获取文章摘要

**方式 B：web_fetch 工具**
- 直接抓取网页内容（Markdown 格式）
- 适合：获取完整文章内容

**方式 C：browser 工具**
- 浏览器自动化访问
- 适合：需要交互的页面

**注意**：由于 SSRF 策略限制，web_fetch 和 browser 可能仍无法直接访问某些外网。此时优先使用 online-search skill。

### 3. 关闭代理

使用 WMI 发送优雅终止信号（允许 Clash Verge 执行配置恢复）：

```powershell
$process = Get-WmiObject -Class Win32_Process | Where-Object { $_.Name -eq "clash-verge.exe" }
if ($process) {
    $process.Terminate()
}
```

**不要使用** `taskkill /F` 强制终止，会导致配置丢失。

## 使用示例

### 示例 1：搜索 Karpathy 的 LLM Wiki 方案

```
1. 启动 Clash Verge
2. 使用 online-search skill 搜索 "karpathy llm wiki site:gist.github.com"
3. 获取搜索结果摘要
4. 关闭 Clash Verge
```

### 示例 2：获取 GitHub Gist 内容

```
1. 启动 Clash Verge
2. 使用 online-search skill 搜索 gist 标题或关键词
3. 从搜索结果中提取关键信息
4. 关闭 Clash Verge
```

## 注意事项

1. **访问完成后立即关闭代理**，避免影响国内网站访问速度
2. **优先使用 online-search skill**，成功率最高
3. **web_fetch 和 browser 可能受 SSRF 限制**，失败时回退到 online-search
4. **不要强制终止 Clash Verge**，使用 WMI Terminate() 方法

## 技术细节

### Clash Verge 进程信息
- 进程名：`clash-verge.exe`
- 桌面快捷方式：`C:\Users\tsc\Desktop\Clash Verge.lnk`
- 关闭方式：WMI Terminate()（优雅退出）

### 为什么不用 taskkill
Clash Verge 退出前需要恢复系统代理设置，强制终止会导致：
- 系统代理设置残留
- 网络连接异常
- 配置文件损坏
