# 07 · 平台模块清单（领域无关基础设施需要哪些模块）

> 回应讨论点 1：系统性回答“这样一个通用基础设施，需要哪些模块”。
> 核心原则：**平台只做“机制”，不做“内容与规则”；金融/社会是使用者实现。**
> 时间与激活域已按讨论拆分为独立模块（见 `11-module-refactor-mapping.md`）。

![平台模块架构（领域无关）](../diagrams/platform-modules.png)

## 0. 三分法（先立边界）

- **① 平台自建**：通用机制，领域无关。
- **② 复用现成**：不重复造轮子，接第三方/开源。
- **③ 使用者实现**：领域内容与规则，平台只提供“挂载点”。

## 1. 核心运行时（① 自建）

| # | 模块 | 一句话职责 |
|---|------|-----------|
| M1 | **AgentRuntime** | 统一递归 agent 抽象：`observe/decide/act/on_fill/children/aggregate`；生命周期与状态绑定 |
| M2 | **Clock** | 逻辑时间 `round/level/step` + 耗时统计（扩展 `ExecutionClock`） |
| M3 | **Scheduler** | 轮循环编排：把 Clock + SyncPolicy + Activation + 四阶段串起来 |
| M4 | **SynchronizationPolicy** | 同步策略：strict（默认）/ deadline / nonblocking（替换硬编码 `ray.get`） |
| M5 | **ActivationController** | 每轮“谁动、给多少预算”，下发 `ActivationSignal`，策略与抽样 |
| M6 | **Signal** | `ActivationSignal / Barrier / Deadline` 等信号类型 |
| M7 | **DecisionEngine** | 观察→决策的具体实现：Rule / LLM / RAG / Composite（插拔） |
| M8 | **CompositeOrchestrator** | 复合 agent 内部编排：Pipeline / Supervisor / Fan-out-Fan-in（可复用 MAF） |

## 2. 世界结构（① 自建）

| # | 模块 | 一句话职责 |
|---|------|-----------|
| M9 | **Topology** | 谁与谁交互：有向图、层级（level）、分组、hub、动态重连 |
| M10 | **SharedState（共享环境状态）** | 通用“世界黑板/共享变量”，版本化+时间戳；领域规则由使用者以 agent/规则函数挂载 |

> 平台**不实现**“市场撮合/订单簿/传播规则”，只提供 M10 共享状态与 M9 拓扑，让使用者在上面实现领域规则。

## 3. 通信与互操作

| # | 模块 | 一句话职责 | 归属 |
|---|------|-----------|------|
| M11 | **MessageBus** | 内部消息：`Info→Message→SimPacket` + 聚合消息 + 兴趣路由 | ① 自建 |
| M12 | **ProtocolBridge** | 跨系统/外部/工具：A2A / MCP / AG-UI | ② 复用 MAF |

## 4. 状态与数据

| # | 模块 | 一句话职责 | 归属 |
|---|------|-----------|------|
| M13 | **StateStore** | 冷/温/热三级状态、快照、checkpoint、断点续跑、幂等 | ① 自建 |
| M14 | **KnowledgeStore / Memory** | RAG 知识、长期记忆、向量检索（分页/摘要/淘汰） | ② 复用向量库 |
| M15 | **Registry** | agent 身份、分组、命名空间、发现、隔离键 | ① 自建 |

## 5. 规模与资源

| # | 模块 | 一句话职责 | 归属 |
|---|------|-----------|------|
| M16 | **ScalePolicy** | 引擎配比、活跃子集/抽样、三级缓存、降级链、配额、成本归因 | ① 自建（策略层） |
| M17 | **LLMGateway** | 路由/限流/缓存/fallback/记账 | ② 复用 LiteLLM/Portkey |

## 6. 治理与观测

| # | 模块 | 一句话职责 | 归属 |
|---|------|-----------|------|
| M18 | **Telemetry** | 指标/trace/采样溯源（OpenTelemetry） | ① 自建 + ② 复用 |
| M19 | **Security / Isolation** | 多租户隔离、鉴权、权限、配额边界 | ① 自建（借 MAF 隔离键思想） |

## 7. 实验与评估

| # | 模块 | 一句话职责 | 归属 |
|---|------|-----------|------|
| M20 | **Config / ScenarioLoader** | 声明式配置、参数化、persona 生成（通用侧） | ① 自建 |
| M21 | **DataCollector / Export** | 数据采集、导出、断点产物；**领域指标由使用者实现** | ① 自建骨架 |

## 8. 明确“③ 使用者实现”的部分（不进平台）

- 领域规则：市场撮合/订单簿、社交传播、感染动力学…
- 领域 agent 行为：金融策略、社会角色、具体 persona…
- 领域消息语义：订单、帖子、评论…
- 领域指标与分析：金融指标、社会指标…
- 领域 persona 生成模板。

## 9. 模块依赖方向

```text
使用者实现（③）
   ▲ 挂在
M20 Config → M3 Scheduler → M5 Activation → M1 AgentRuntime → M7 DecisionEngine
               │ 用 M2 Clock · M4 SyncPolicy · M6 Signal
               ▼
       M9 Topology · M10 SharedState · M11 MessageBus
               │
               ▼
       M13 StateStore · M12 ProtocolBridge(②) · M17 LLMGateway(②)
               │
               ▼
       M15 Registry · M19 Security · M16 ScalePolicy · M18 Telemetry · M21 DataCollector
```

## 10. 自查问题（确保没把领域塞进平台）

对每个模块问：**“如果使用者用它做社会模拟（没有市场、没有订单），这个模块还成立吗？”** 成立→留平台；不成立→改造或移到“使用者实现”。

## 11. 待确认

1. 模块清单是否有**可合并/多余**的？（例如 M8 并入 M7、M14 并入 M13。）
2. 是否还有**缺失**模块？（事件系统？可视化/控制台？场景打包/发布？）
3. M10 SharedState 作为“世界黑板”是否认同？还是希望“环境/世界”本身也做成抽象模块？
