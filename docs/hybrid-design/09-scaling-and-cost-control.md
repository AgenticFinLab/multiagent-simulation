# 09 · 规模化与成本控制

> 目标：同一场景，在 10² / 10³ / 10⁵ 三档规模下，用**同一套代码、不同策略配置**运行，把“LLM 调用数、token 量、并发、成本”变成受控变量。

## 1. 规模策略（Scale Policy）配置

在 `simulation.yml` / 新增 `scale-policy.yml` 中声明：

```yaml
scale_policy:
  engine_mix:          # 各引擎占比（默认按规模档自动）
    rule: 0.95
    llm: 0.04
    rag: 0.01
  group:
    enabled: true
    size: 50           # 每组成员数（聚合比 10~100）
  llm:
    active_ratio: 0.05     # 每轮真正调 LLM 的 agent 比例
    sample_policy: importance  # uniform / importance / stratified
    max_calls_per_turn: 2000 # 硬上限（熔断）
    token_budget_per_agent: 2000
  cache:
    prompt_prefix: true
    semantic: true
    result: true
  degradation:
    on_timeout: rulellm -> rule
    on_budget: llm -> rule
```

规模档（L1/L2/L3）自动给出默认值，场景作者可覆盖。

## 2. 减少 LLM 调用次数（最有效）

1. **活跃子集**：只有“值得思考”的 agent 调 LLM（例如：价格异动、新闻事件、组内 leader）。
2. **重要性抽样**：按持仓规模/影响力/异常度加权抽样，其余用规则跟随。
3. **分层聚合**：leader 调 LLM，成员跟随（见 `06`）。
4. **决策缓存复用**：同状态/同事件直接复用结果。
5. **跨轮复用**：低频决策（“每天”一次意图），高频执行（逐 tick）走规则——MarketSim 的战略/执行解耦。

## 3. 减少 token 量与单次成本

1. **共享前缀**：所有 agent 共享同一 system/persona 前缀，最大化 provider prompt 缓存（可省 ~90% 前缀成本）。
2. **压缩上下文**：只给最近关键事件 + 摘要，不给全量历史（Harness 的 context compaction）。
3. **结构化输出**：决策用 schema 约束，减少自由文本 token 与解析回退。
4. **模型分级路由**：简单决策用小模型，复杂决策用大模型（LLM Router 思想）。

## 4. 三级缓存（数据支撑）

| 缓存 | 命中对象 | 收益 |
|------|----------|------|
| prompt 前缀缓存 | 相同 system/persona/历史前缀 | 前缀 token 省至多 ~90% |
| 语义缓存 | 语义相似的状态/查询 | 消除 20–40% 调用 |
| 结果缓存 | 完全相同输入 | 消除 10–25% 调用 |

> 三者叠加可把整体推理成本降 60–70%（Microsoft Learn 的实测指导值）。**在模拟场景里，大量 agent 共享 persona/市场摘要，语义缓存收益尤其高。**

## 5. 降级链（Degradation）

```text
LLM ──(超时/超预算/限流)──> RuleLLM ──(仍不可行)──> Rule（默认/跟随行为）
```
- 降级在 `DecisionEngine` 层统一触发，记录 `degradation_reason`，用于审计与质量评估。
- 保证世界始终前进，不被个别慢/贵 agent 卡死。

## 6. 异步与流水线（B5）

- **异步预取**：上一轮就为下一轮提交 LLM 决策（投机执行），世界推进不空等。
- **批处理**：LLM 请求进队列，worker 按 batch 提交（提升 provider 吞吐、摊薄成本）。
- **慢路径隔离**：LLM/检索走无状态 worker 池，规则/撮合走 actor，互不阻塞。
- 可复现性补偿：即便异步，结果仍按 `(round, level, seq)` 归位落盘，保持逻辑顺序。

## 7. 通信规模化（B2，配合 07）

- 分层 hub + 兴趣路由 + 聚合消息，把 O(N²) 降到 O(N·k + m²)。
- 组内 k、组数 m 由 group size 控制。

## 8. 成本归因与熔断

- 每 agent / group / 租户累计 token 与调用次数，超配额熔断或降级。
- 控制面实时统计：`calls/turn、tokens/turn、cache_hit_rate、degrade_rate、cost/turn`。
- 目标：**成本可预测、可预算、可归因**，而不是“跑完才知道花了多少”。

## 9. 三档规模的目标画像

| 指标 | L1 几十 | L2 几千 | L3 几十万 |
|------|---------|---------|-----------|
| LLM agent 比例 | 高 | 中（活跃子集） | 极低（抽样/leader） |
| 消息路由 | 直连为主 | group + 部分 hub | 分层 hub + 兴趣路由 |
| 状态 | 全内存 | 温层 + 冷层 | 冷层为主 + 压缩 |
| 缓存 | 可选 | 全开 | 全开且语义优先 |
| 可复现 | 强 | 强（缓存辅助） | 规则路径强、LLM 路径统计对齐 |

## 10. 与“不解决 LLM 加速”的边界

我们**不优化单次推理**，而是通过调度/批处理/缓存/降级让“对黑盒模型的使用”达到规模经济。若未来更换更快的 serving，本设计不变——因为引擎与网关之间的接口只关心 `latency/throughput/rate-limit/cost`。
