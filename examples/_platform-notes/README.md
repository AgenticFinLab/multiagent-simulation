# 平台实现参考笔记（Platform Implementation Notes）

> 本目录是对已有工作/论文的**深入总结与讨论**，目的是在写代码前“清楚、明确、正确地理解每一个部分”，并**逐条映射到 `masim/platform/*/base.py` 契约**，指导后续实现。
> 本目录**只含文档，不含实现代码**；场景发现只扫描 `configs/`，因此本目录不影响任何运行。

## 阅读顺序（建议）

1. 先读 `10-implementation-mapping.md` 的**总映射表**（每篇文章 → 机制 → 平台模块 → 实现要点）。
2. 再按需要精读 01–09。

## 文档索引

| 文件 | 主题 | 主要映射到的平台模块 |
|------|------|----------------------|
| `01-scaling-and-hybrid-engines.md` | 规模化 + LLM/规则混合（OASIS、FLAME GPU） | ScalePolicy · DecisionEngine · ActivationController |
| `02-distributed-execution.md` | 分布式执行与消息（AgentSociety、Ray、Matrix） | Scheduler · MessageBus · Clock |
| `03-market-microstructure.md` | 市场微观结构（TwinMarket、MarketSim） | 领域层示例 · SharedState · Topology |
| `04-financial-llm-agents.md` | 金融 LLM agent（FinAgent、FinMem、FinGPT、QuantAgents、FinRobot） | DecisionEngine · StateStore（记忆） |
| `05-generative-agent-memory.md` | 记忆-反思-规划（Generative Agents、1000 People、MemGPT/Letta） | StateStore · AgentRuntime |
| `06-orchestration-patterns.md` | 编排范式（AutoGen、LangGraph、CrewAI、Agents SDK、MetaGPT、ChatDev、AgentVerse） | CompositeOrchestrator · Aggregator |
| `07-protocols-and-interop.md` | 协议与互操作（MCP/A2A/AG-UI/ANP/ACP） | ProtocolBridge · MessageBus |
| `08-abm-and-gpu-platforms.md` | 传统 ABM 与 GPU（NetLogo/Repast/GAMA/Mesa/FLAME GPU） | Topology · Scheduler |
| `09-evaluation-benchmarks.md` | 评估基准（SocialBench、AgentBench、stylized facts、MoA、辩论） | Telemetry · DataCollector |
| `10-implementation-mapping.md` | 总映射表 | 全部 |

## 使用约定

- 每个文件末尾都有「对实现的启示」，用 `→ masim/platform/<module>/base.py` 形式标注落点。
- 所有“规模/性能数字”都是论文报告值，用于**量级判断**，不是我们平台的承诺值。
- 领域（金融/社会）相关内容只在 `03`/`04` 出现，且**只作领域层参考**，不进入平台内核。
