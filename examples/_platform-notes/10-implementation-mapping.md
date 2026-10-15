# 10 · 总映射表（论文 → 机制 → 平台模块 → 实现要点）

> 一页总览：把 01–09 的结论压成实现清单。写代码前先查这张表。

## 1. 总映射

| 来源 | 关键机制 | 平台模块 | 第一版实现要点 |
|------|----------|----------|----------------|
| OASIS | LLM+规则混合、时间引擎、推荐 hub、显式动作空间 | ScalePolicy · Clock · RoutePolicy · DecisionEngine | 引擎 mix + 活跃子集；动作显式化 |
| FLAME GPU | GPU 规则洪流 | DecisionEngine(Rule) | 后期优化，不进第一版 |
| AgentSociety | Ray+MQTT、引擎核/执行核分离、分组 | Scheduler · MessageBus | 有状态 actor + 无状态 worker |
| Ray | Task+Actor、对象存储 | AgentRuntime/DecisionEngine 实现载体 | actor 有状态、worker 无状态 |
| Matrix | 无状态 worker + 队列 | DecisionEngine(LLM/RAG) | 队列去耦 |
| TwinMarket | BDI + 撮合 + 社交 + 行为偏差 | 领域层（不进内核） | 领域示例 |
| MarketSim | 战略/执行分层 + CDA + stylized facts | Scheduler（低频决策/高频执行）+ 领域层 | 分层是领域实例 |
| FinAgent/FinMem | 分层记忆、双层反思 | StateStore + KnowledgeStore | 冷温热 + 检索 |
| FinGPT | RLSP 金融小模型 | 模型层（可选） | 不进内核 |
| QuantAgents/FinRobot | 会议协作 / Financial CoT | CompositeOrchestrator + Aggregator | 顺序 + 统计聚合 |
| Generative Agents | 记忆流/三信号检索/反思/规划 | StateStore + AgentRuntime | 记忆检索 + 反思节流 |
| 1000 People | 访谈校准 + 专家反思 | Config（persona 生成） | L1 逐人、L3 模板 |
| MemGPT/Letta | 分页/摘要/检索/淘汰 | StateStore 三级 | 冷温热 |
| MetaGPT/ChatDev/Agents SDK/AgentVerse/AutoAgents | SOP/对话链/handoff/模块化/自动生成 | CompositeOrchestrator（后续实现） | 第一版仅顺序+Fan-out |
| AutoGen/LangGraph/CrewAI | 群聊/状态图 checkpoint/HITL/层级 | CompositeOrchestrator + StateStore | 复用思想，MAF 后续接 |
| MCP/A2A/AG-UI/ANP/ACP | 标准协议互操作 | ProtocolBridge（薄适配，复用 MAF） | 内部总线 + 外部协议 |
| NetLogo/Repast/GAMA/Mesa | Model/Scheduler/Space | Topology · Scheduler | 建模概念 |
| SocialBench/AgentBench/stylized facts | 分层评估 | Telemetry · DataCollector | 个体+群体两层 |
| MoA / Multi-Agent Debate | 分层聚合 / 辩论 | Aggregator/Composite（后续） | 第一版不做 |

## 2. 第一版实现优先级（结合 D1–D10）

1. `agent` / `decision`：AgentRuntime + DecisionEngine（Rule 先做，LLM 接网关）。
2. `runtime`：Clock + Scheduler + SynchronizationPolicy（strict）。
3. `activation`：ActivationController + ActivationPolicy（AllActive 默认）。
4. `message`：MessageBus（最简三层消息 + RoutePolicy）。
5. `state`：StateStore（冷温热 + checkpoint + scope）。
6. `topology` / `world` / `registry`：Topology + SharedState + Registry。
7. `composite`：Aggregator（统计 + LLM 摘要）+ CompositeOrchestrator（顺序 + Fan-out）。
8. `scale`：ScalePolicy + DegradationPolicy（LLM→Rule 降级）。
9. ProtocolBridge（复用 MAF，薄适配）。

## 3. 一句话提醒

**先让“机制”跑通（Rule 路径端到端），再接 LLM、再接协议、再接规模策略。** 不要一开始就把所有引擎/协议/缓存都叠上。
