# HEARTBEAT.md

<!-- OpenClaw 心跳任务配置 -->
<!-- 格式：## cron: <表达式> <描述> -->

## cron: 0 8 * * 1 📊 工业通信行业周报

### 任务说明
每周一上午8点生成工业通信行业周报

### 监控范围

**国际厂商**：西门子(Siemens)、Moxa(摩莎)、研华(Advantech)、菲尼克斯(Phoenix Contact)、Hirschmann(Belden)、魏德米勒(Weidmüller)、伊顿(Eaton)、ATEN

**国内厂商**：华为、中兴、锐捷、新华三(H3C)、东土、普天信科、三旺、兆越、科动、迈威、子午线、光路科技、有人物联

### 报告内容
1. 产品动态：新产品发布、版本更新
2. 市场动态：财报、战略合作
3. 技术趋势：TSN、工业以太网新技术
4. 行业事件：展会、论坛、认证
5. 竞品信息：重点竞品动态

### 可用数据源 (官网URL)

**国际厂商**：
- Moxa: https://www.moxa.com/en/about-us/news-events
- 研华 (Advantech): https://www.advantech.com/en/about/corporate-news
- 西门子 (Siemens): https://www.siemens.com/global/en/company/news.html
- Hirschmann (Belden): https://www.belden.com/about/press-room
- 菲尼克斯: https://www.phoenixcontact.com/en-us/about-us/news-and-events

**国内厂商**：
- 东土: https://www.kyland.com/news/product (更新较慢)
- 三旺: https://www.sanway.cn (网站访问不稳定)
- 迈威: http://www.mieware.com
- 锐捷: https://www.ruijie.com.cn
- 华为: https://www.huawei.com/cn/news

### 输出
- 报告：`memory/industry-weekly-{date}.md`
- 索引：`memory/industry-trends.md`

### 执行方式
1. 使用 browser 工具逐个访问上述URL
2. 抓取新闻/动态页面内容
3. 提取关键信息生成结构化周报
4. 保存至 memory 目录

---

## cron: 0 9 * * 1 📊 创新技术双周扫

### 任务说明
每两周一次，扫描工业通信与嵌入式新技术动态

### 监控重点
- TSN新技术、标准更新、芯片动态
- 工业以太网新协议（OPC UA、MQTT）
- AI/边缘计算在工业通信的应用
- 国内工业通信新技术初创公司

### 输出
- 摘要：`memory/tech-innovation-{date}.md`

---

## cron: 0 9 * * 1 📈 周一竞品动态汇总

### 任务说明
每周一上午9点汇总重点竞品产品更新

### 重点关注
- 东土、三旺、迈威新产品发布
- Hirschmann、Moxa 产品线更新
- 国内厂商价格/策略变化

---

# 预留任务位

<!-- 可在此添加更多定时任务 -->
<!-- ## cron: <表达式> <描述> -->
