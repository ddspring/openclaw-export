# IPv6 Neighbor表项定时老化 - 修改设计文档

**文档版本**：V1.0  
**编制日期**：2026-03-05  
**适用内核**：Linux 4.14.76  
**功能需求**：支持命令行配置IPv6邻居表项按指定时间老化，而非随机老化

---

## 1. 背景与目标

### 1.1 问题描述

Linux内核默认实现中，IPv6 Neighbor表项的可达时间（Reachable Time）采用**随机化机制**：

```
实际老化时间 = base_reachable_time × (0.5 ~ 1.5)
```

即：配置30秒可达时间，实际老化时间在15秒~45秒之间随机。

**问题影响**：
- 工业交换机场景下，无法精确预测邻居表项老化时间
- 网络调试和故障排查困难
- 与其他网络设备时间配合不精确

### 1.2 需求目标

- 支持通过命令行配置IPv6邻居表项的**精确老化时间**
- 保持与现有随机化行为的**向后兼容**
- 提供灵活的配置方式（全局/接口级）

---

## 2. 现状分析

### 2.1 现有机制

#### 2.1.1 随机化函数

**文件**：`net/core/neighbour.c`  
**函数**：`neigh_rand_reach_time()`

```c
unsigned long neigh_rand_reach_time(unsigned long base)
{
    return base ? (prandom_u32() % base) + (base >> 1) : 0;
}
```

**说明**：返回 `[0.5×base, 1.5×base)` 区间内的随机值

#### 2.1.2 sysctl配置接口

| 配置项 | 路径 | 默认值 | 说明 |
|--------|------|--------|------|
| base_reachable_time | /proc/sys/net/ipv6/neigh/\<iface\>/base_reachable_time | 30秒 | 基础可达时间（jiffies） |
| base_reachable_time_ms | /proc/sys/net/ipv6/neigh/\<iface\>/base_reachable_time_ms | 30000ms | 毫秒级配置 |

#### 2.1.3 代码调用位置

| 文件 | 行号 | 场景 |
|------|------|------|
| `net/core/neighbour.c` | 806-807 | 定时器周期更新 |
| `net/core/neighbour.c` | 1493-1494 | 创建新邻居项 |
| `net/core/neighbour.c` | 1556-1557 | 初始化默认参数 |
| `net/ipv6/ndisc.c` | 1838-1840 | sysctl写入时更新 |

#### 2.1.4 定时器机制

邻居表项老化定时器在 `neigh_timer_handler()` 中处理，关键逻辑：

```c
// net/core/neighbour.c:932-940
if (time_after(jiffies, neigh->confirmed + neigh->parms->reachable_time)) {
    // 邻居项超时，进入不可达状态
    neigh_update(neigh, NULL, NUD_FAILED, ...);
}
```

`reachable_time` 字段即为 `neigh_rand_reach_time()` 的返回值。

---

## 3. 方案设计

### 3.1 设计原则

1. **最小修改原则**：尽量减少对内核代码的改动
2. **向后兼容**：默认保持现有随机化行为
3. **配置灵活性**：支持全局配置和接口级配置
4. **接口统一**：与现有sysctl接口风格一致

### 3.2 总体方案

**新增一个sysctl配置项**：控制是否使用精确老化时间

| 配置项 | 值 | 行为 |
|--------|-----|------|
| use_reachable_time | 0（默认） | 使用随机化时间（现有行为） |
| use_reachable_time | 1 | 使用精确指定时间 |

### 3.3 数据结构设计

#### 3.3.1 neighbor.h 修改

**文件**：`include/net/neighbour.h`

在 `enum` 中新增配置索引：

```c
enum {
    NEIGH_VAR_MCAST_PROBES,
    NEIGH_VAR_UCAST_PROBES,
    NEIGH_VAR_APP_PROBES,
    NEIGH_VAR_MCAST_REPROBES,
    NEIGH_VAR_RETRANS_TIME,
    NEIGH_VAR_BASE_REACHABLE_TIME,
    NEIGH_VAR_DELAY_PROBE_TIME,
    NEIGH_VAR_GC_STALETIME,
    NEIGH_VAR_QUEUE_LEN_BYTES,
    NEIGH_VAR_PROXY_QLEN,
    NEIGH_VAR_ANYCAST_DELAY,
    NEIGH_VAR_PROXY_DELAY,
    NEIGH_VAR_LOCKTIME,
    /* 新增配置项 */
    NEIGH_VAR_USE_REACHABLE_TIME,  // ← 新增
#define NEIGH_VAR_DATA_MAX (NEIGH_VAR_USE_REACHABLE_TIME + 1)
    // ... 原有后续项 ...
};
```

> **说明**：将 `USE_REACHABLE_TIME` 插入到 `NEIGH_VAR_LOCKTIME` 之前，确保 `NEIGH_VAR_DATA_MAX` 正确计算。

#### 3.3.2 neigh_parms 结构体

`struct neigh_parms` 无需修改，通过 `data[]` 数组和 `NEIGH_VAR()` 宏访问：

```c
// 访问方式
NEIGH_VAR(p, USE_REACHABLE_TIME)  // 读取
NEIGH_VAR_SET(p, USE_REACHABLE_TIME, val)  // 写入
```

---

## 4. 详细设计

### 4.1 neighbour.c 修改

#### 4.1.1 新增可达时间获取函数

**位置**：`net/core/neighbour.c`（约115行附近）

```c
/**
 * neigh_get_reach_time - 获取邻居项可达时间
 * @parms: 邻居参数块
 *
 * 根据 use_reachable_time 配置返回：
 * - 精确时间（配置为1时）
 * - 随机化时间（配置为0时，默认）
 */
static inline unsigned long neigh_get_reach_time(struct neigh_parms *parms)
{
    if (NEIGH_VAR(parms, USE_REACHABLE_TIME))
        return NEIGH_VAR(parms, BASE_REACHABLE_TIME);
    
    return neigh_rand_reach_time(NEIGH_VAR(parms, BASE_REACHABLE_TIME));
}
```

#### 4.1.2 替换调用点

需要替换以下位置的 `neigh_rand_reach_time()` 调用：

| 行号 | 原始代码 | 替换后 |
|------|----------|--------|
| ~806 | `p->reachable_time = neigh_rand_reach_time(...)` | `p->reachable_time = neigh_get_reach_time(p)` |
| ~1493 | 同上 | 同上 |
| ~1556 | 同上 | 同上 |
| ~2099 | 同上 | 同上 |
| ~3085 | 同上 | 同上 |

> **注意**：`reachable_time` 字段本身存储的是计算后的值（随机化或精确），每次配置变更时需要重新计算。

#### 4.1.3 新增初始化值

在 `neigh_table_init()` 或相关初始化函数中，设置默认值：

```c
/* 默认使用随机化 */
NEIGH_VAR_INIT(&tbl->parms, USE_REACHABLE_TIME, 0);
```

---

### 4.2 ndisc.c 修改

#### 4.2.1 添加默认值初始化

**位置**：`net/ipv6/ndisc.c`（约127行附近）

在 `ndisc_devdefault_sysctl_defaults()` 中添加：

```c
static int __net_init ndisc_devdefault_sysctl_defaults(struct net *net)
{
    struct ipv6_dev_sysctl_table *p;
    // ... 现有代码 ...

    // 设置默认值
    p->tbl[NEIGH_VAR_USE_REACHABLE_TIME].data = 0;  // 默认随机化
}
```

#### 4.2.2 添加sysctl表项

**位置**：`net/ipv6/ndisc.c`（sysctl表定义处）

在 `ipv6_neigh_sysctl_table` 中添加新项：

```c
{
    .procname = "use_reachable_time",
    .data     = &NEIGH_VAR(idev->nd_parms, USE_REACHABLE_TIME),
    .maxlen   = sizeof(int),
    .mode     = 0644,
    .proc_handler = proc_dointvec_minmax,
    .extra1   = &zero,
    .extra2   = &one,
},
```

#### 4.2.3 处理配置变更

**位置**：`net/ipv6/ndisc.c` - `ndisc_ifinfo_sysctl_change()` 函数

在现有处理逻辑后添加：

```c
else if (strcmp(ctl->procname, "use_reachable_time") == 0)
    ret = neigh_proc_dointvec(ctl, write, buffer, lenp, ppos);

if (write && ret == 0 && dev && (idev = in6_dev_get(dev)) != NULL) {
    // 现有逻辑...
    
    // 当 use_reachable_time 变更时，重新计算 reachable_time
    if (ctl->data == &NEIGH_VAR(idev->nd_parms, USE_REACHABLE_TIME))
        idev->nd_parms->reachable_time =
            neigh_get_reach_time(idev->nd_parms);
}
```

---

### 4.3 arp.c 修改（可选，IPv4同步）

如IPv4也需要支持精确老化时间，需同步修改 `net/ipv4/arp.c`：

- 添加 `use_reachable_time` 配置项
- 使用相同的 `neigh_get_reach_time()` 函数

---

## 5. 用户接口设计

### 5.1 procfs 接口

```
/proc/sys/net/ipv6/neigh/<interface>/use_reachable_time
/proc/sys/net/ipv6/neigh/default/use_reachable_time
```

### 5.2 配置示例

```bash
# 1. 查看当前配置（默认0，表示使用随机化）
cat /proc/sys/net/ipv6/neigh/eth0/use_reachable_time
# 输出: 0

# 2. 启用精确时间模式
echo 1 > /proc/sys/net/ipv6/neigh/eth0/use_reachable_time

# 3. 配置基础老化时间（秒）
echo 60 > /proc/sys/net/ipv6/neigh/eth0/base_reachable_time

# 4. 验证：此时邻居表项将在精确60秒后老化，不再随机
```

### 5.3 全局默认配置

```bash
# 设置全局默认使用精确时间
echo 1 > /proc/sys/net/ipv6/neigh/default/use_reachable_time

# 所有新建接口默认使用精确时间
```

---

## 6. 测试计划

### 6.1 单元测试

| 测试项 | 预期结果 |
|--------|----------|
| use_reachable_time=0 | 保持现有随机化行为 |
| use_reachable_time=1 | 精确按配置时间老化 |
| 切换模式 | 新表项按新模式生效 |

### 6.2 功能测试

| 测试项 | 验证方法 |
|--------|----------|
| 配置立即生效 | 写入配置后新建邻居表项验证 |
| 老化时间精确性 | 记录邻居项创建和删除时间 |
| 多接口独立配置 | 验证不同接口配置独立生效 |

### 6.3 性能测试

- 大量邻居表项（>10000）场景下性能
- 高频配置变更压力测试

---

## 7. 影响评估

### 7.1 文件修改清单

| 序号 | 文件路径 | 修改类型 | 预估行数 |
|------|----------|----------|----------|
| 1 | `include/net/neighbour.h` | 修改 | +5行 |
| 2 | `net/core/neighbour.c` | 修改 | +15行，修改6处 |
| 3 | `net/ipv6/ndisc.c` | 修改 | +20行 |
| 4 | `net/ipv4/arp.c` | 可选 | +15行 |

### 7.2 兼容性影响

| 方面 | 影响评估 |
|------|----------|
| 向后兼容 | ✅ 默认配置保持现有行为 |
| 应用程序 | ✅ 现有配置接口不变 |
| 协议合规 | ✅ 符合RFC 4861（随机化为建议性） |

### 7.3 风险评估

| 风险 | 等级 | 缓解措施 |
|------|------|----------|
| 配置项命名冲突 | 低 | 使用明确的全名 use_reachable_time |
| 性能影响 | 低 | 仅在配置变更时计算一次 |
| 边界条件 | 低 | base_reachable_time=0 时保持原逻辑 |

---

## 8. 文档更新

### 8.1 技术文档

- 更新《产品技术规格书》
- 更新《命令行配置手册》

### 8.2 变更记录

| 版本 | 日期 | 修改人 | 说明 |
|------|------|--------|------|
| V1.0 | 2026-03-05 | 研发博士 | 初始版本 |

---

## 9. 备选方案

### 9.1 方案B：新增独立配置项（非替换）

- 添加 `reachable_time_exact` 配置项
- 同时保留原有 `base_reachable_time`
- 使用方式：`echo 60 > reachable_time_exact`

**优点**：完全不影响现有逻辑  
**缺点**：配置项冗余

### 9.2 方案C：基于Netlink接口

通过 `ip -6 neigh` 命令扩展实现

**优点**：用户界面更友好  
**缺点**：实现复杂度高

---

**文档结束**
