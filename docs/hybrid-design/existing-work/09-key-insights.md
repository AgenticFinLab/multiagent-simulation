# 09 · 核心洞察（供深入讨论）

> 这是审查完已有工作后，提炼出的、可讨论的 10 条判断。每条都附“证据”与“可讨论点”。

## I1. 规模与 LLM 占比成反比（最硬的一条）
- 证据：OASIS 10⁶ 用 LLM+rule 混合；纯 LLM 只在 ≤10³ 级。
- 判断：**“全 LLM”不是规模方案，混合引擎才是**。
- 可讨论点：各规模档的 LLM 占比上限怎么定？

## I2. “世界”与“决策”必须两层
- 证据：OASIS 时间引擎、AgentSociety 引擎核/执行核分资源、MarketSim 战略/执行解耦、MASim 四阶段。
- 判断：**时间推进/市场撮合必须与 LLM 延迟解耦**。
- 可讨论点：同步时间步 + 异步预取的边界在哪？

## I3. 消息分发必须 hub/瓶颈，不能全对全
- 证据：OASIS 推荐 hub、AgentSociety MQTT+分组、Project Sid PIANO 信息瓶颈。
- 判断：**大规模通信靠聚合/路由，不靠全连接**。
- 可讨论点：hub 分几层、聚合比多大？

## I4. 分布式有三条成熟路线，Ray actor 最适合“有状态金融 agent”
- 证据：MASim/AgentSociety 用 Ray actor；Matrix 用无状态 worker+队列；AgentScope 用 JVM 无状态。
- 判断：**有状态（持仓/记忆）用 actor，无状态（LLM 调用）用 worker 池**。
- 可讨论点：actor 与 worker 的粒度如何切？

## I5. 行为真实性靠“偏差注入 + 记忆反思”，不靠 prompt
- 证据：TwinMarket 注入 disposition/lottery 偏差；Park 的记忆-反思；EconAgent 记忆反思。
- 判断：**行为金融偏差 + 记忆机制是金融 agent 的“像人”关键**。
- 可讨论点：偏差库如何标准化？

## I6. 复合/sub-agent 已有成熟范式，但都在“应用级”
- 证据：TradingAgents（12 专家）、CrewAI hierarchical、MAF Harness/Workflow、Project Sid 多流。
- 判断：**复合 agent 内部编排可直接借用 MAF，但要推广到“世界内大规模”**。
- 可讨论点：复合 agent 的递归深度与聚合 schema。

## I7. 状态/持久化是规模化的隐形门槛
- 证据：LangGraph checkpoint-per-superstep、AgentScope 多租户隔离、MAF session/isolation、MASim 断点续跑。
- 判断：**checkpoint + 幂等 + 隔离键是几十万 agent 可运行的前提**。
- 可讨论点：checkpoint 粒度（轮/层/sub-agent）与成本平衡。

## I8. 标准协议（A2A/MCP/AG-UI）是“整齐、标准”的现成答案
- 证据：MAF 与 AgentScope 都原生支持 A2A/MCP。
- 判断：**外部互操作不要自造协议，用 A2A/MCP/AG-UI**。
- 可讨论点：内部是否也走协议，还是仅外部走协议？

## I9. 成本控制有成熟三板斧：缓存 + 降级 + 配额
- 证据：前缀缓存 ~90%、语义缓存 20–40%、结果缓存 10–25%、合计 60–70%（MS Learn）。
- 判断：**成本是可工程化控制的，不是“跑完才知道”**。
- 可讨论点：语义缓存在多大程度上会破坏行为异质性？

## I10. 已有工作的共同空白 = 我们的价值位
- 证据：对比表（D1–D8）无人全占；MASim 与 MAF 缺口完全互补。
- 判断：**“金融世界内核 + 标准协议互操作 + 几十到几十万的异构降级”是一个尚未被整体做出来的组合**。
- 可讨论点：这个价值位是否值得作为本项目的一页定位？

## 附：这 10 条洞察如何进入后续讨论
- I1–I4 决定**规模与运行时的骨架**。
- I5–I6 决定**agent 的行为与内部结构**。
- I7–I9 决定**工程可靠性与成本**。
- I10 决定**项目定位与范围**。

> 建议：下一轮我们逐条讨论 I1→I10，先对齐“哪些成立、哪些要改、哪些有新证据”，再谈具体设计。
