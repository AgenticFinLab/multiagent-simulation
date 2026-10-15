# 01 · 规模化与 LLM/规则混合引擎

> 核心问题：几十万 agent 时，为什么不能全用 LLM？混合引擎怎么设计？

## 1. 为什么“全 LLM”不可扩展

- 一次 LLM 决策 ≈ 秒级、有 token 成本；规则决策 ≈ 微秒级、几乎零成本。
- 若每轮每个 agent 都调 LLM，则调用次数 = N：N=10⁵ 时每轮 10⁵ 次调用，延迟与成本同时爆炸。
- 结论：**LLM 调用总量必须是受控变量**，而不是随 N 线性增长。

## 2. OASIS（百万级混合模拟）—— 最直接的证据

- 出处：NeurIPS 2024 / arXiv 2411.11581；开源 camel-ai/oasis。
- 做到了：模拟 Twitter/Reddit 上**多达 100 万用户**，研究信息传播、群体极化、羊群效应。
- 关键机制：
  1. **LLM + 规则混合**：绝大多数行为由规则承担，LLM 只处理需要语义理解的部分。
  2. **时间引擎**：时间步推进，1 步 = 3 分钟，**显式把时间推进与 LLM 推理延迟解耦**。
  3. **信息分发 hub = 推荐系统**：兴趣推荐 + 热度推荐，用户通过推荐发现内容，避免全对全传播。
  4. **23 种动作**：动作空间显式化（关注/评论/转发…），可控、可统计。

### 对实现的启示
- `→ masim/platform/decision/base.py`：`DecisionEngine` 必须支持 `Rule` 与 `LLM` 两种 kind，且 `supports(budget, deadline)` 供路由。
- `→ masim/platform/runtime/base.py`：`Clock`（逻辑时间）与 `Scheduler` 分离——时间推进不等待 LLM。
- `→ masim/platform/message/base.py`：信息分发用 hub/兴趣路由（`RoutePolicy`），不搞全对全。
- `→ masim/platform/activation/base.py`：绝大多数 agent 本轮不被激活，只有少数走 LLM（活跃子集）。

## 3. FLAME GPU（百万规则 agent 的另一种极端）

- 出处：FLAME GPU 2；开源。
- 做到了：把 agent 函数编译为 CUDA kernel，agent 状态驻留 GPU 显存，消息在 GPU 内传递；**一块工作站级 GPU 可实时模拟百万级规则 agent**。
- 适用：**规则/数值型 agent**（不含 LLM）。

### 对实现的启示
- L3（几十万）里绝大多数 agent 是规则型，可参考“批量规则引擎”思路，但不作为第一步。
- 关键边界：**规则洪流走 GPU/向量化，LLM 决策走 CPU worker 池**——两者是不同执行路径，不要混在同一 actor 里。

## 4. 混合引擎的通用结论

| 规模 | LLM 占比 | 依据 |
|------|----------|------|
| 10² | 高（可全 LLM） | 高保真 |
| 10³ | 中（活跃子集） | 分组/抽样 |
| 10⁵ | 极低（抽样/leader） | OASIS 式混合 |

> 这条“规模—LLM 占比反比”曲线，是 `ScalePolicy` 的默认起点。

## 5. 落到平台契约

- `DecisionEngine.kind` 决定走 Rule/LLM/RAG/Composite。
- `ScalePolicy.engine_mix(agent_id, round)` 决定“谁这轮用哪种引擎”。
- `ActivationController.select()` 决定“谁这轮真的动”。
- `ScalePolicy` + `DegradationPolicy` 决定“超预算/超时如何降级”。
