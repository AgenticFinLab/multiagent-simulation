# 04 · 目标混合架构蓝图

## 1. 一句话架构

> **MASim 当“世界内核”，MAF 当“决策与协议能力层”，中间用四个抽象接口（AgentRuntime / DecisionEngine / MessageBus / StateStore）粘合，形成一个六层的混合运行时。**

## 2. 六层结构

```text
┌─────────────────────────────────────────────────────────────────────────┐
│ L5 控制面 Control Plane（低频）                                           │
│   实验编排 · 场景/规模配置 · 调度策略 · 配额 · 可观测 · 评估             │
├─────────────────────────────────────────────────────────────────────────┤
│ L4 状态与存储 StateStore（冷/温/热）                                      │
│   actor 状态 · 快照/checkpoint · session/isolation · 向量记忆 · 对象存储 │
├─────────────────────────────────────────────────────────────────────────┤
│ L3 通信与协议 MessageBus + Protocols                                      │
│   内部消息总线(Info→Message→SimPacket+聚合/兴趣路由)                      │
│   协议桥：A2A(agent↔agent) · MCP(agent↔工具) · AG-UI(人机)             │
├─────────────────────────────────────────────────────────────────────────┤
│ L2 决策引擎 DecisionEngine（异构、可插拔、可降级）                         │
│   RuleEngine · LLMEngine(经 MAF chat client+批处理/缓存/降级)            │
│   RAGEngine · CompositeEngine(MAF Workflow/Harness/supervisor)          │
├─────────────────────────────────────────────────────────────────────────┤
│ L1 统一 Agent 抽象 AgentRuntime                                          │
│   统一契约：observe → decide → act(+on_fill) + 可选 sub-agents           │
│   MASim GeneralPlayer 与 MAF Agent/Workflow.as_agent() 都映射到此         │
├─────────────────────────────────────────────────────────────────────────┤
│ L0 世界内核 World Engine（MASim）                                          │
│   时间/轮次推进 · 市场撮合(CDA/orders) · 拓扑层级 · 四阶段循环             │
│   Ray actor 分布式（PlayerPersona 推广为通用 AgentActor）                │
└─────────────────────────────────────────────────────────────────────────┘
         │                                    │
   控制面（低频，人/策略可见）          数据面（高频，性能关键）
```

## 3. 四个核心抽象接口（粘合层）

这是“整齐、标准”的关键——所有层只依赖这四个接口，不互相依赖具体实现。

### 3.1 AgentRuntime（统一 agent 运行时）
```
observe(observation, prev_result) -> None
decide() -> decision_payload          # 由 DecisionEngine 具体执行
act(decision_payload) -> action
on_fill(action, quantity, bid_price) -> None   # 成交后钩子（MASim 契约保留）
children() -> list[AgentRuntime]               # 复合 agent 的子 agent（可为空）
```
- 规则 agent：`decide()` 直接跑规则。
- LLM agent：`decide()` 提交给 LLMEngine（异步预取）。
- 复合 agent：`decide()` 由 CompositeEngine 编排 children，再汇总。

### 3.2 DecisionEngine（决策引擎）
```
async decide(context, budget, policy) -> Decision
```
- 四个实现：Rule / LLM / RAG / Composite。
- 统一“降级与预算”入口：engine 自己决定能否在当前 budget/latency 内完成，否则抛 `Degrade` 信号。
- LLMEngine 内部使用 MAF 的模型客户端（Chat Completions/Responses）统一供应商，再叠批处理/缓存/降级。

### 3.3 MessageBus（消息总线）
```
publish(info, sender, targets, route_policy) -> ...
deliver(message, target) -> ...
```
- 内部实现沿用 MASim `Info → Message → SimPacket` 三层模型，扩展“聚合消息 + 兴趣路由”。
- 对外协议桥把外部 A2A/MCP 流量翻译成内部消息，把内部 agent 暴露为 A2A 服务。

### 3.4 StateStore（状态与存储）
```
save(agent_id, state) / load(agent_id) -> state
checkpoint(round, level) / restore(round, level)
scope(isolation_key) -> store_view
```
- 冷/温/热三级；多租户用 isolation key 作用域化（借鉴 MAF）。

## 4. 控制面 / 数据面职责边界

| 关注点 | 控制面 | 数据面 |
|--------|--------|--------|
| 频率 | 低频 | 高频 |
| 内容 | 配置、策略、配额、观测、评估 | actor、消息、状态、LLM 调用 |
| 扩展方式 | 单实例/少数实例 | 水平扩展（Ray worker） |
| 失败影响 | 实验暂停 | 可重试/可恢复 |

## 5. 两种引擎的物理部署关系

```text
控制面（driver）
   │ load_config + 规模策略
   ▼
Ray Cluster（Head + N Workers）
   ├─ AgentActor（有状态，per agent 或 per group）
   │     ├─ AgentRuntime（统一契约）
   │     └─ DecisionEngine（本地规则 or 提交远程 LLM）
   ├─ LLM Worker Pool（无状态，从队列拉取）
   │     └─ LLMEngine → 批处理网关 → 模型供应商（黑盒）
   ├─ Protocol Gateways（可选，MAF 自托管）
   │     ├─ A2A host（把内部复合 agent 暴露为远端服务）
   │     ├─ MCP host（把工具/知识暴露给 agent）
   │     └─ AG-UI（人机交互/调试）
   └─ StateStore（冷/温/热 + checkpoint）
```

## 6. 与 MAF 的职责对应

| 混合架构层 | MASim 现有 | MAF 提供 | 说明 |
|-----------|-----------|----------|------|
| L0 世界内核 | GeneralSimulator / 四阶段 / 市场 / 拓扑 | —（MAF 不管世界） | 保留，不重写 |
| L1 Agent 抽象 | GeneralPlayer | `Agent` / `Workflow.as_agent()` | 统一到一个 `AgentRuntime` |
| L2 决策引擎 | Rule/LLM/RuleLLM/Rag 四机制 | chat client、Workflow、Harness、middleware | 新增 CompositeEngine |
| L3 通信协议 | Info/Message/SimPacket | A2A / MCP / AG-UI / hosting | 内部总线 + 外部协议桥 |
| L4 状态存储 | HistoryBuffer / StorageProxy | SessionStore、isolation、checkpoint | 统一 StateStore |
| L5 控制面 | configs + analysis.py | telemetry、declarative、DevUI | 扩展规模策略与配额 |

## 7. 为什么这样设计（回答“灵活、专业、整齐、标准”）

- **灵活**：引擎、协议、存储、agent 形态都是插件，可单独替换或新增。
- **专业**：关键问题（B1–B9）都在架构中有明确归属层，不靠“补丁”。
- **整齐**：六层 + 四接口，依赖单向（上层依赖下层接口，不反向）。
- **标准**：外部交互全部走 A2A/MCP/AG-UI 标准协议，内部有明确的三层消息模型与状态契约。
