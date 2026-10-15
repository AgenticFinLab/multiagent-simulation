# 02 · 分布式执行与消息

> 核心问题：几十万有状态 agent，如何分布式跑？消息如何不 O(N²)？

## 1. AgentSociety（Ray + MQTT + 分组）

- 出处：ACL 2025 Industry / arXiv 2502.08691；清华。
- 做到了：10k+ agent、平均 500 次交互/天、共 500 万次交互；3 万 agent 在 24×A800 上“快于墙钟时间”，性能随 LLM 算力线性增长。
- 关键机制：
  1. **Ray 分布式 + MQTT 高性能消息系统**。
  2. **异步模拟架构 + agent 分组**。
  3. **Mind–Behavior 耦合**：agent 有心智层（情绪/需求/动机/认知）与行为层。
  4. 明确把**模拟引擎核**与**agent 执行核**分资源（64 核：32 引擎 + 32 agent）。

### 对实现的启示
- `→ masim/platform/runtime/base.py`：Scheduler 是“引擎核”，DecisionEngine/AgentRuntime 是“执行核”——两者可分开扩资源。
- `→ masim/platform/message/base.py`：内部高频消息需要高效总线；分组 + 路由避免全对全。

## 2. Ray（Task + Actor）

- 核心：**Task（无状态）+ Actor（有状态）**；动态任务图；actor 方法远程调用、串行执行；对象存储传递中间结果。
- 这是我们“有状态 agent 用 actor、无状态 LLM 调用用 worker 池”的工程依据。

### 对实现的启示
- `AgentRuntime` 的有状态实现 = Ray actor（复用现有 `PlayerPersona` 的推广）。
- `DecisionEngine` 的 LLM/RAG 调用 = 无状态 worker 池 + 队列。

## 3. Meta Matrix（无状态 worker + 队列）

- 出处：Meta，Ray-native，面向合成数据生成。
- 做到了：**无状态 agent 作为 Ray actor 从分布式队列拉任务**（peer-to-peer 调度），token 吞吐 2–15×（相比中心编排），质量相当。

### 对实现的启示
- LLM 调用这“无状态重活”应抽成 worker 池 + 队列；有状态（持仓/记忆）留在 actor。这正是 `DecisionEngine`（无状态）与 `AgentRuntime`（有状态）分离的理由。

## 4. 分布式执行的三条成熟路线对比

| 路线 | 代表 | 适合 |
|------|------|------|
| 有状态 actor | MASim / AgentSociety | 有持仓/记忆的 agent |
| 无状态 worker + 队列 | Matrix | 纯 LLM 吞吐 |
| JVM 无状态水平扩展 | AgentScope | 生产服务 |

## 5. 落到平台契约

- `Scheduler.run_round()` 是分布式调度入口；`Clock` 给逻辑时间；`SynchronizationPolicy` 给“怎么等”。
- `MessageBus` 是第一版内部消息；聚合消息/兴趣路由后续补（D10）。
- `StateStore` 负责状态与断点，使 actor 可恢复。
