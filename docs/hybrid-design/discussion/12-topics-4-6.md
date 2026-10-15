# 12 · 重新讨论备份的 4–6 号问题

> 前 1–3 号（平台定位 / 异构激活 / 时间语义）已充分讨论并冻结。现在回到之前备份的 4–6 号。

## 4. 协议边界（内部总线 vs 外部协议）

**已定（D1）**：内部高频通信走 MessageBus，跨系统/外部/工具走 A2A/MCP/AG-UI。
**已写契约**：`masim/platform/message/base.py`（MessageBus / Info / Message / SimPacket / RoutePolicy）。

仍需讨论：

1. **ProtocolBridge 要不要写 base.py？** 我倾向**不写**——它是“复用 MAF 的薄适配层”，不是平台自建模块；只需要一个 `ProtocolBridge` 适配器约定：内部 agent → A2A 服务（AgentCard）、外部 A2A agent → AgentRuntime、MCP server → 工具。
2. **MessageBus 的扩展点**：聚合消息（AggregateMessage）与兴趣路由（RoutePolicy）是否纳入第一版契约，还是先只做最简 `Info→Message→SimPacket` + `RoutePolicy` 接口，聚合/兴趣路由后续补？
3. **鉴权边界**：A2A 的 `AgentCard` 只做发现、不做授权；多用户宿主绑定鉴权——这条是否需要在 ProtocolBridge 契约里显式声明为强制项？

## 5. 复合 agent 的深度与聚合

**已定（D2）**：递归嵌套 + 聚合可插拔。
**已写契约**：`composite/base.py`（ChildResult / Aggregator / CompositeOrchestrator）+ `agent/base.py`（children/aggregate）。

仍需讨论：

1. **嵌套深度软约束**：`max_depth` / `max_children` / `max_total_agents` 三个参数是否够？默认给多少？
2. **聚合默认实现**：先做「统计聚合」和「LLM 摘要聚合」两个，还是先只做统计聚合？
3. **MAF 映射**：`CompositeOrchestrator` 的第一版实现是否直接复用 MAF `Workflow`（顺序/交接/群聊 + checkpoint），还是先做一个最简顺序编排、MAF 后续接？

## 6. 已有工作的补充范围

**已完成**：14 篇审查文档 + 分类地图 + 协议全景（含 OASIS/AgentSociety/MarketSim/TwinMarket/FinAgent/FinMem/FinGPT/QuantAgents/FinRobot/MetaGPT/ChatDev/Agents SDK/AgentVerse/AutoAgents/MemGPT/LiteLLM/FLAME GPU/NetLogo/Repast/协议）。

仍需讨论：

1. 是否还需补充**评估基准**（SocialBench / AgentBench / 金融 stylized-facts 基准）与**多智能体辩论/混合（MoA / multi-agent debate）**两类？
2. 是否认为已有审查已足够支撑进入实现，后续按需再补？

---

> 建议逐个回应；尤其第 4 题的「ProtocolBridge 是否写 base.py」、第 5 题的「聚合默认实现先做几个」会直接影响下一步实现范围。
