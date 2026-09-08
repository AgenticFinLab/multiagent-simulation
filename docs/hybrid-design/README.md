# MASim × Microsoft Agent Framework 混合架构设计

> 本目录是对「把 MASim 与 Microsoft Agent Framework（MAF）结合，构成一个支持从几十、几千到几十万 agent 的混合模拟环境」这一命题的**完整分析与设计文档集**。
> 每个 agent 可能是纯代码、大模型驱动，甚至内部包含多个 sub-agent；目标是**灵活、专业、整齐、标准**。
> 明确边界：**不讨论我们无法自行解决的部分**（例如大模型底层推理/服务加速、自研 GPU 内核等），只在其上做架构、编排、调度、成本与协议设计。

## 阅读导引（按依赖顺序）

| 文件 | 主题 | 一句话说明 |
|------|------|-----------|
| `01-scenario-and-requirements.md` | 场景与需求 | agent 光谱、规模等级、交互模式、生命周期与评估目标 |
| `02-key-problems-and-bottlenecks.md` | 关键问题与瓶颈 | 计算/通信/状态/时序/成本/工程六类瓶颈，明确哪些我们解决、哪些不解决 |
| `03-design-principles.md` | 设计原则 | 10 条指导原则，贯穿后续所有设计 |
| `04-target-architecture.md` | 目标架构蓝图 | 六层混合架构 + 控制面/数据面分离，MASim 为内核、MAF 为能力层 |
| `05-agent-taxonomy-and-hybrid-engines.md` | Agent 分类与混合引擎 | 纯代码/规则/LLM/RAG/复合五类，统一契约 + 异构引擎 |
| `06-hierarchy-and-subagents.md` | 层级与 sub-agent | supervisor-worker、分组 leader、嵌套/递归、harness/workflow-as-agent |
| `07-communication-and-protocols.md` | 通信与协议 | 内部消息总线、兴趣路由、A2A/MCP/AG-UI 桥接 |
| `08-state-storage-and-durability.md` | 状态/存储/持久化 | 冷热状态、快照、断点续跑、幂等、多租户隔离 |
| `09-scaling-and-cost-control.md` | 规模化与成本 | 从几十到几十万的分层分片、批处理、缓存、降级、配额 |
| `10-related-work-and-lessons.md` | 已有工作与经验 | OASIS / AgentSociety / MarketSim / Matrix / MASim / MAF 对比与借鉴 |
| `11-open-questions-and-roadmap.md` | 开放问题与路线图 | 待决策点、风险、分阶段落地路径 |

## 一页结论（TL;DR）

1. **不要做一个“大一统 Agent 框架”**，而是做一个**分层混合运行时**：MASim 继续当“世界引擎”（时间推进、市场撮合、拓扑、Ray 分布式、状态/消息），MAF 当“决策与协议能力层”（统一 agent/workflow 抽象、A2A/MCP/AG-UI、session/isolation、中间件与可观测）。
2. **规模靠“异构 + 分层 + 降级”**：几十个 agent 可以全 LLM；几千个要分组、批处理、异步；几十万个必须让绝大多数 agent 走规则/行为/向量路径，LLM 只作用于活跃子集或抽样子集。
3. **子 agent 靠“统一 Agent 抽象 + 递归组合”**：一个复合 agent 内部可以用 MAF 的 `Workflow` / `Harness Agent` / supervisor-worker 表达，对外仍是一个 agent；子 agent 可以是本地函数、Ray actor，也可以是远端 A2A 服务。
4. **通信靠“分层 hub + 兴趣路由 + 标准协议”**：内部用轻量消息总线避免 O(N²) 广播，对外用 A2A（agent↔agent）、MCP（agent↔工具/知识）、AG-UI（人机）。
5. **成本与稳定性靠“预算、缓存、降级、幂等、快照”**：prompt/语义/结果三级缓存 + LLM→RuleLLM→Rule 降级链 + token 配额 + 轮级 checkpoint/断点续跑。
6. **“整齐、标准”落在边界清晰的分层与显式契约上**：统一 `AgentRuntime`/`DecisionEngine`/`MessageBus`/`StateStore` 四个抽象，所有引擎与协议都实现同一套接口。

## 术语

- **Agent（智能体）**：一个拥有身份、状态、观察/决策/行动能力的计算实体。
- **复合 Agent / sub-agent**：一个 agent 内部再包含若干子 agent（可递归）。
- **决策引擎（Decision Engine）**：把“观察 → 决策”这一步具体化的运行时（Rule / LLM / RAG / Composite）。
- **世界引擎（World Engine）**：时间推进、市场撮合、拓扑、消息投递、状态落盘等与“谁在做决策”无关的部分。
- **分组 / hub**：为压缩消息规模而引入的聚合节点（leader、coordinator、推荐 hub）。
- **降级（degradation）**：在预算/延迟/配额约束下，把高成本引擎切换到低成本引擎或抽样执行。

## 参考链接

- MASim 本仓库：`../structure.md`、`docs/framework-contract.md`
- Microsoft Agent Framework：https://github.com/microsoft/agent-framework
- OASIS：https://arxiv.org/abs/2411.11581
- AgentSociety：https://arxiv.org/abs/2502.08691
- MarketSim：https://icml.cc/virtual/2026/poster/65297
- Meta Matrix：https://github.com/facebookresearch/matrix（Ray-native 多智能体调度）
