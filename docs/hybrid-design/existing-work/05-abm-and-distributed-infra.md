# 05 · 传统 ABM 与分布式基础设施

## 1. Mesa（传统基于 agent 的建模）

- 核心概念：`Model` + `Agent` + `Scheduler` + `Space`。
- 时间推进：整数 tick；实验性 `experimental.devs` 支持**离散事件调度 + 连续时间**，可做混合 ABM-DEVS。
- 可视化：`ModularServer` + 浏览器（Tornado + WebSocket），start/stop/step 控制。
- 现状局限：单机、同步、面向“模型研究”而非“大规模 LLM 模拟”。

### 启示
- 经典 ABM 的“Model/Scheduler/Space 分离”仍然正确——MASim 的四阶段本质是它的分布式强化版。
- “时间步 + 离散事件混合”是处理异构时间尺度的正统思路。

## 2. Ray（分布式计算底座）

- 核心：**Task（无状态） + Actor（有状态）**。
- 动态任务图：remote function/actor 方法在输入就绪时自动触发。
- **Actor**：状态化计算，方法可远程调用、串行执行。
- 分布式对象存储（object store）传递中间结果。

### 启示
- MASim 已经建在 Ray 上；Ray 是“几十万有状态 agent”的合理底座。
- “有状态 actor + 无状态 task/worker”正是我们 P3 原则的工程依据。

## 3. Meta Matrix（Ray-native 多智能体调度）

- 核心：**无状态 agent 作为 Ray actor，从分布式队列拉任务**（peer-to-peer 调度，而非中心编排）。
- 效果：token 吞吐 2–15×（相比中心编排基线），质量相当。
- 用途：合成数据生成等重吞吐场景。

### 启示
- **队列去耦 + 无状态 worker** 是提升 LLM 吞吐的有效结构。
- 有状态 agent（需要持仓/记忆）不能直接套用，但“LLM 调用”这部分可以抽成无状态 worker 池。

## 4. 本类共性结论

| 层 | 工具 | 给我们的定位 |
|----|------|--------------|
| 建模范式 | Mesa | Model/Scheduler/Space 概念保持 |
| 分布式执行 | Ray | 有状态 actor 底座（已用） |
| LLM 吞吐 | Matrix 模式 | 无状态 worker + 队列 |
| 消息 | MQTT/总线 | 大规模消息分发（AgentSociety 已用） |

**一句话**：分布式与 ABM 的工程底座已成熟，我们的增量不在“重新发明调度”，而在“把金融世界 + 标准协议 + 异构决策”干净地叠上去。
