# 10 · 已有工作与经验

> 本节回答“历史上/已有工作怎么做的、有什么经验、当前框架做到了什么地步”，并落到“我们能借鉴什么”。

## 1. 大规模 LLM 多智能体模拟

### 1.1 OASIS（Open Agent Social Interaction Simulations on One Million Agents）
- 来源：NeurIPS 2024 / arXiv 2411.11581；开源 camel-ai/oasis。
- 做到了什么：**LLM + 规则混合**，模拟 Twitter/Reddit 上**多达 100 万用户**；23 种动作；动态社交网络与帖子环境；**时间引擎以 3 分钟为一个 time step**；用**推荐系统作为信息分发 hub**（兴趣推荐 + 热度推荐）。
- 经验借鉴：
  1. “混合引擎 + 时间步”是百万级的关键；
  2. **信息分发不要全对全，而要一个 hub 按兴趣/热度路由**；
  3. 动作空间显式化（23 个），便于可控与可统计。

### 1.2 AgentSociety
- 来源：ACL 2025 Industry / arXiv 2502.08691；清华。
- 做到了什么：**Ray 分布式 + MQTT 高性能消息系统**，10k+ agent、500 万次交互；异步模拟架构 + agent 分组机制；宣称 3 万 agent 可在 24×A800 上“快于墙钟时间”，性能随 LLM 算力线性增长。
- 经验借鉴：
  1. **Ray + 消息总线 + 分组** 是大规模社会模拟的成熟组合；
  2. 异步架构是吞吐关键；
  3. 明确把“模拟引擎核”与“agent 执行核”分资源（64 核中 32 核引擎 + 32 核 agent）。

### 1.3 MarketSim（ICML 2026）
- 来源：ICML 2026 poster 65297；15,000+ 参与者。
- 做到了什么：**分层多 agent 架构，把“战略推理”与“高频执行”解耦**——AI 基金经理读市场信息形成交易意图，交易员 agent 在纳秒级 NASDAQ 式连续双边拍卖市场执行；接入 12k 新闻/政策/财报；复现 5 个市场 stylized facts，平均 MAPE 3.48%。
- 经验借鉴：**战略/执行分层** 直接解决“LLM 慢、市场快”的矛盾，是金融场景的核心模式。

### 1.4 Meta Matrix（Ray-native 多智能体）
- 来源：Meta，Ray-native，面向合成数据生成的多智能体调度。
- 做到了什么：**无状态 agent 作为 Ray actor 从分布式队列拉任务**（peer-to-peer 调度，而非中心编排），token 吞吐 2–15×。
- 经验借鉴：**有状态 actor + 无状态 worker + 队列去耦**，是我们 P3 原则的直接来源。

## 2. 生成式智能体的行为基础

- **Generative Agents（Park et al.）**：profile / memory / reflection / plan 的经典四模块，是“人形”agent 的记忆-反思基础。
- **Generative Agent Simulations of 1,000 People**：千人级、面试校准的 agent，强调 persona 保真与校准。
- 经验借鉴：**记忆采用“存储 + 检索 + 反思”**，而非全量回放；**persona 需要校准**（我们 10⁵ 规模只能统计校准，不能逐人面试）。

## 3. 我们自己的两个底座

### 3.1 MASim（本仓库）
- 已做到：Ray actor + 拓扑层级 + 四阶段（execute/collect/dispatch/record）+ 三层消息（Info/Message/SimPacket）+ 四机制（Rule/LLM/RuleLLM/Rag）+ `on_fill` 契约 + 断点续跑 + 实验产物。
- 定位：**世界引擎内核**。规模化的“分布式执行”与“市场/拓扑/状态”已具备，缺的是“异构引擎统一、分层聚合、协议桥、成本控制”。

### 3.2 Microsoft Agent Framework（MAF）
- 已做到：多语言 .NET/Python/Go；`Agent` / `Workflow`（图 + checkpoint + HITL + `as_agent()`）/ `Harness Agent`；A2A（AgentCard/任务模型/跨语言）、MCP、AG-UI/Responses 托管；session store + isolation key；middleware + OpenTelemetry；多供应商。
- 定位：**决策/编排/协议/治理能力层**。它不管“世界怎么运转”，正好与 MASim 互补。

## 4. 横向对比表

| 系统 | 规模 | 核心机制 | 对混合架构的启示 |
|------|------|----------|------------------|
| OASIS | 10⁶ | LLM+rule 混合、时间引擎、推荐 hub | 混合引擎、信息 hub、时间步 |
| AgentSociety | 10⁴ | Ray + MQTT + 分组 + 异步 | 消息总线、分组、异步 |
| MarketSim | 1.5×10⁴ | 战略/执行分层 + CDA | 分层解耦 LLM 与高频撮合 |
| Matrix | 集群级 | 无状态 actor + 队列 | 有状态/无状态分离 |
| MASim | 10²~10³ | Ray actor + 拓扑四阶段 + 三层消息 | 世界内核（保留） |
| MAF | 应用级 | Agent/Workflow/A2A/MCP/session | 能力层（借用） |

## 5. 可复用的经验清单（浓缩）

1. 百万级靠 **LLM+rule 混合**，不是全 LLM。
2. 大规模消息靠 **hub/兴趣路由/分组**，不是全对全。
3. 吞吐靠 **异步 + 队列 + 无状态 worker**。
4. 金融靠 **战略/执行分层**。
5. 记忆靠 **检索+反思+压缩**，不是全量回放。
6. 工程化靠 **checkpoint/幂等/isolation**。
7. 成本靠 **前缀/语义/结果三级缓存 + 降级 + 配额**（实测可省 60–70%）。
8. 标准互操作靠 **A2A/MCP/AG-UI**。

## 6. 当前框架“还差什么”（我们要补的）

- MASim：缺统一异构引擎、分层聚合、协议桥、成本/降级控制。
- MAF：缺“世界推进 + 大规模扇入扇出 + 市场撮合 + 10⁵ 级 actor 编排”。
- 二者结合恰好互补，混合架构的增量集中在“四个接口 + 分层聚合 + 规模策略 + 协议桥”。
