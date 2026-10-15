# 09 · 评估基准与推理增强

> 核心问题：怎么评估“模拟/agent 像不像、好不好”？哪些基准可借鉴？

## 1. 社会性 / 个体行为基准

### SocialBench（ACL 2024 Findings）
- 首个系统评估**角色扮演 agent 的社会性**，分个体层与群体层。
- 规模：500 个角色、6,000+ 问题、30,800 多轮对话。
- 关键发现：**个体层强不代表群体层强**——群体涌现需要单独测。
- 启示：我们的评估也要分“个体行为对齐”与“群体涌现（stylized facts）”两层。

### SocietyBench（2026）
- 端到端基准：一行事件主题 → 收集五平台新闻/社交 → 时间线 → 评估 LLM/agent 预测社会演化。
- 启示：可借鉴“事实层 + 舆论层分离”的时间线表示。

## 2. 通用 agent 能力基准

### AgentBench（ICLR 2024，清华）
- 8 个交互环境（OS/数据库/知识图谱/游戏等），评估 LLM-as-Agent 的多步规划、工具、观测处理。
- 启示：通用能力基准用于选模型；领域评估仍要自己建。

## 3. 金融市场 stylized facts（领域层评估）

- 来源：MarketSim（5 个 stylized facts + 5 个价格统计指标，MAPE 3.48%）、TwinMarket（肥尾等）。
- 典型 stylized facts：**波动聚集、胖尾收益、动量/反转、成交量-波动相关、杠杆效应**。
- 启示：这是“场景有效性”的**领域层**验收标准——进程成功 ≠ 场景有效（与我们现有验收一致）。

## 4. 多智能体推理增强（复合 agent 的候选机制）

### Mixture-of-Agents（MoA）
- 分层结构：**proposer（多个参考模型并行产出）→ aggregator（一个强模型汇总）**。
- 提升质量但成本/延迟高；衍生 RouteMoA 用动态路由降本。
- 启示：`Aggregator` 的一种“LLM 摘要聚合”实现可直接借鉴 MoA 的分层聚合思想。

### Multi-Agent Debate（MAD）
- 多 agent 多轮辩论提升推理；但收益**高度依赖 regime**，且成本高。
- 优化：S2-MAD（打破 token 壁垒）、Confidence-Guided Adaptive Debate、Consensus-Awarded Debate（省 API 调用 40–64%）。
- 启示：辩论是 `CompositeOrchestrator` 的可选高级实现，**不是第一版**；先做顺序 + Fan-out/Fan-in。

## 5. 落到平台契约

- 个体/群体分层评估 → `Telemetry` + `DataCollector` 的指标设计。
- stylized facts → 领域层评估，不进内核。
- MoA/辩论 → `Aggregator` / `CompositeOrchestrator` 的后续可选实现（D10：先不做）。
