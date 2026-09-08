# 已有工作 · 全面审查与核心把握

> 本目录是「MASim × MAF 混合架构」项目**第一步**的交付物：只审查、整理、思考**已有工作**，不进入我们自己的设计。
> 目标：对已有工作形成**全面、核心、准确**的把握，为后续深入讨论与设计提供共同的事实基础。

## 分类地图（我们如何切分这个领域）

```text
已有工作
├─ A. 大规模社会模拟器（10⁴~10⁶）
│     OASIS · AgentSociety · Project Sid
├─ B. 金融/经济模拟器（10¹~10⁴）
│     TwinMarket · MarketSim · TradingAgents · EconAgent · CompeteAI
├─ C. 生成式智能体行为基础（10⁰~10³）
│     Generative Agents (Park 2023) · 1000 People (Park 2024)
├─ D. 通用多智能体框架/编排（应用级）
│     AutoGen · LangGraph · CrewAI · AgentScope · CAMEL
├─ E. 传统 ABM 与分布式基础设施
│     Mesa · Ray · Matrix
└─ F. 两个底座（本项目将结合的双方）
      MASim（我们） · Microsoft Agent Framework
```

## 文档索引

| 文件 | 覆盖 | 配套图 |
|------|------|--------|
| `01-large-scale-social-simulators.md` | OASIS / AgentSociety / Project Sid | `oasis-architecture`、`agentsociety-architecture` |
| `02-financial-economic-simulators.md` | TwinMarket / MarketSim / TradingAgents / EconAgent / CompeteAI | `twinmarket-architecture`、`marketsim-architecture` |
| `03-generative-agent-foundations.md` | Park 2023 / 1000 People | `generative-agents-memory` |
| `04-agent-frameworks.md` | AutoGen / LangGraph / CrewAI / AgentScope / CAMEL | `autogen-langgraph-patterns` |
| `05-abm-and-distributed-infra.md` | Mesa / Ray / Matrix | 文字为主 |
| `06-masim-base.md` | 我们的 MASim | 复用 `../../../diagrams/masim-architecture.png` |
| `07-maf-base.md` | Microsoft Agent Framework | 复用 `../../../diagrams/maf-architecture.png` |
| `08-comparative-matrix.md` | 横向对比总表（8 维度） | `taxonomy` |
| `09-key-insights.md` | 提炼的核心洞察（供讨论） | 文字 |

## 一页核心结论（审查后）

1. **规模的分水岭是「是否全 LLM」**：百万级系统（OASIS）无一例外采用「LLM + 规则混合」；纯 LLM 只在 10²~10³ 级可行。
2. **「世界推进」与「agent 决策」在成熟系统中是两层**：OASIS 有时间引擎，MarketSim 有战略/执行解耦，AgentSociety 把模拟引擎核与 agent 执行核分资源——这正是 MASim 已具备、MAF 不具备的部分。
3. **大规模消息/信息分发靠 hub 或总线，不靠全对全**：OASIS 用推荐系统做信息 hub，AgentSociety 用 MQTT 消息总线 + 分组。
4. **分布式执行有三条成熟路线**：Ray actor（MASim/AgentSociety）、Ray 无状态 worker + 队列（Matrix）、JVM 无状态水平扩展（AgentScope）。
5. **agent 行为学有两条经典范式**：Park 的记忆-反思-规划；1000 People 的访谈校准 + 专家反思。规模化后前者退化、后者不可行，需统计校准。
6. **编排框架（AutoGen/LangGraph/CrewAI）解决「小规模高质量协作」，不解决「大规模模拟」**；两者的能力边界清晰，不可混用。
7. **MAF 是 AutoGen/SK 的收敛，强在协议（A2A/MCP/AG-UI）、会话/隔离、可观测与图工作流**，弱在「没有世界推进与市场撮合」——正好由 MASim 补齐。
8. **已有工作的共同空白**：没有人把「金融世界内核 + 标准协议互操作 + 从几十到几十万的异构降级」作为一个整体做出来。这正是本项目的价值位。

## 如何阅读

- 先看 `08-comparative-matrix.md` 的对比表建立全景，再按 A→F 顺序精读。
- 每个系统的文档都遵循同一结构：**定位 → 核心架构 → 关键机制 → 规模/成本事实 → 对我们的启示**。
- 图表在 `diagrams/`，均为 SVG 源 + PNG 导出，可编辑。
