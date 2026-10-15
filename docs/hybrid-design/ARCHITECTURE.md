# 总体架构（讨论收敛版）

> 本文把讨论阶段 D1–D8 的结论整合成一份权威架构，作为后续「接口契约 / 实现」的基线。
> 平台定位：**领域无关的通用多智能体模拟基础设施**；金融/社会由使用者实现。

## 1. 一句话架构

**一个领域无关的多智能体运行时：使用者用通用原语实现领域 agent 与世界规则；平台负责时间、激活、通信、状态、规模、协议与观测。**

![总体架构图](diagrams/platform-overall-architecture.png)

## 2. 三层边界（谁做什么）

```text
③ 使用者实现（不进平台）        领域规则 · 领域 agent · 领域消息语义 · 领域指标 · persona
   ▲ 挂在
① 平台自建（21 个通用模块）     见 §3
   ▲ 依赖
② 复用现成（不重复造）           LLM 网关 · MAF 协议桥 · 向量库 · 对象存储
```

## 3. 21 个平台模块（详见 discussion/07）

- 核心运行时：AgentRuntime · Clock · Scheduler · SynchronizationPolicy · ActivationController · Signal · DecisionEngine · CompositeOrchestrator
- 世界结构：Topology · SharedState
- 通信：MessageBus · ProtocolBridge(②)
- 状态：StateStore · KnowledgeStore(②) · Registry
- 规模：ScalePolicy · LLMGateway(②)
- 治理：Telemetry · Security/Isolation
- 实验：Config · DataCollector

![平台模块架构](diagrams/platform-modules.png)

## 4. 一轮的运行时流程（核心）

```text
Config(M20) 加载场景
   → Scheduler(M3) 推进一轮 round
       ├─ Clock(M2) 标记 round/level/step（逻辑时间，非墙钟）
       ├─ SynchronizationPolicy(M4) 决定“怎么等”（默认 strict）
       ├─ 对每个拓扑层级 level：
       │     ├─ ActivationController(M5) 判定“谁动”，下发 ActivationSignal(M6)
       │     ├─ 被激活的 AgentRuntime(M1)
       │     │     └─ DecisionEngine(M7) Rule/LLM/RAG/Composite(M8) 产出决策
       │     ├─ MessageBus(M11) 按 Topology(M9) 投递消息
       │     └─ StateStore(M13) 落盘 / checkpoint
       └─ SharedState(M10) 更新共享世界状态（领域规则由使用者挂载）
   → DataCollector(M21) 采集 · Telemetry(M18) 观测
```

![一轮运行时流程](diagrams/platform-runtime-flow.png)

## 5. 关键接口边界（后续要写契约的对象）

| 接口 | 一句话 |
|------|--------|
| `AgentRuntime` | 统一递归 agent：`observe/decide/act/on_fill/children/aggregate` |
| `DecisionEngine` | 观察→决策：Rule / LLM / RAG / Composite |
| `ActivationPolicy` | 谁动、给多少预算 |
| `SynchronizationPolicy` | 怎么等：`strict`（默认）等 |
| `Aggregator` | 复合 agent 汇总子结果（可插拔） |
| `Signal` | ActivationSignal / Barrier / Deadline |
| `MessageBus` | 内部消息 `Info→Message→SimPacket` + 聚合/兴趣路由 |
| `StateStore` | 冷/温/热 + 快照 + 续跑 + 隔离 |

## 6. 已冻结决策索引

| 编号 | 结论 |
|------|------|
| D1 | 内部通信走总线；跨系统/外部/工具才走 A2A/MCP/AG-UI |
| D2 | 复合 agent：接口 + 递归嵌套 + 聚合可插拔 |
| D3 | 平台无任何领域层，金融/社会由使用者实现 |
| D4 | 逻辑时间（round/level），不模拟墙钟；同步由 Scheduler 管 |
| D5 | 激活 = 平台独立模块 ActivationController + ActivationSignal |
| D6 | 平台只定义时钟/信号/同步策略接口；等待/异步是使用者策略 |
| D7 | 时间/激活域拆成 Clock/Scheduler/SyncPolicy/Activation/Signal 五模块，最小改造 |
| D8 | Signal 与 Activation 同域 `masim/activation/`；SyncPolicy 默认仅 strict |

## 7. 与两个底座的关系

- **MASim**：提供世界侧的成熟实现（Ray actor、四阶段、拓扑层级、三层消息、断点续跑），按 D7 做最小改造，抽成上述模块。
- **MAF**：提供能力侧的复用（A2A/MCP/AG-UI 协议桥、Workflow/Harness 复合编排、Session/Isolation、Telemetry 思想）。

## 8. 下一步

1. 为 §5 的 8 个接口写第一版**接口契约**（输入/输出/生命周期/错误语义）。
2. 补一张「一轮运行时流程」的正式图。
3. 之后进入实现（按 D7 的 5 步顺序）。
