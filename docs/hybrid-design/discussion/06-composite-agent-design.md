# 06 · 复合 agent 的详细设计逻辑与架构

> 回应讨论点 5：明确“复合 agent / 子 agent / 聚合”的设计逻辑与架构。这是本模块的第一版详细设计（非全平台设计）。

## 1. 设计目标

让一个 agent 的内部“由若干子 agent 组成”，对外却**仍然是一个 agent**；子 agent 可以再嵌套（递归）；聚合方式可插拔。

## 2. 核心抽象：统一递归契约

```text
AgentRuntime
  ├─ observe(observation, prev_result)
  ├─ decide() -> Decision            # 由绑定的 DecisionEngine 执行
  ├─ act(decision) -> action
  ├─ on_fill(action, qty, price)     # 领域钩子（仅交易型需要）
  ├─ children() -> list[AgentRuntime]   # 子 agent（叶子为空）
  └─ aggregate(child_results) -> summary  # 聚合接口（可插拔）
```

关键点：
- **叶子和复合都实现同一个 `AgentRuntime`** → 递归天然成立。
- `decide()` 对叶子 = 单次规则/LLM；对复合 = 编排 children + 汇总。
- 外部（世界/市场/消息系统）**看不到** children，只看得到“一个 agent”。

## 3. 复合引擎 CompositeEngine 的决策流程

```text
decide(context)
  1. 规划 / 分派（可选 LLM/规则）     → 决定“本轮哪些子 agent 需要跑、以什么顺序”
  2. 并行/串行执行 children.decide()  → 每个子 agent 各自产出 Decision
  3. aggregate(child_results)        → 把子结果汇总成父决策依据
  4. 父决策                         → 输出父级 Decision
```

四步里，**1 可选、3 可插拔、2 是核心执行、4 是输出**。规划可简化成“全部子 agent 都跑”或“按依赖图跑”。

## 4. 聚合接口（可插拔，回应 D2）

```text
Aggregator
  ├─ aggregate(child_results: list[ChildResult]) -> AggregatedSummary
  └─ schema() -> {统计量 + 离群样本 + 溯源引用}
```

- 默认实现 A：**统计聚合**（数量、均值、极值、分位、多数意见）——便宜、确定。
- 默认实现 B：**LLM 摘要聚合**——贵但能表达“综合研判”。
- 未来按需：**层级聚合、语义聚合、多模态聚合**。
- 每个 `ChildResult` 带 `child_id / decision / confidence / evidence / 版本`，保证可溯源。

## 5. 子 agent 的三种部署位置（运行时不关心）

| 位置 | 形态 | 适用 | 代价 |
|------|------|------|------|
| 本地函数/协程 | 纯规则子逻辑 | 便宜、无状态 | 无隔离 |
| 本地 Ray actor | 有状态子 agent | 需并行/有状态 | 调度开销 |
| 远端 A2A 服务 | 跨语言/跨团队 | 重决策/复用 | 网络+协议开销 |

> 因为三者都实现 `AgentRuntime`，父 agent 的编排/聚合代码**不因位置而变**（位置只是“绑定”时的配置）。

## 6. 嵌套与深度（回应 D2）

- 深度**不设硬上限**，只做软约束：`max_depth`、`max_children`、`max_total_agents` 可配置，防止误配失控。
- 递归终止：`children()` 为空（叶子）。

## 7. 生命周期与状态

- 父 agent 状态 = 自身状态 + 对子 agent 状态的**引用/摘要**（不复制全文）。
- 子 agent 状态由子 agent 自己管理（各自 `AgentRuntime` + 各自 StateStore 视图）。
- 父 `decide()` 结束即完成一次“复合决策”；不要求子 agent 常驻（可临时创建/复用）。

## 8. 三个内置组织模式（先实现这三个）

| 模式 | 结构 | 适合 |
|------|------|------|
| Pipeline | 子 agent 串行，前一个输出喂给后一个 | 分析→风控→组合 |
| Supervisor | 一个“经理”动态分派/验证，其余是 worker | 基金公司、监管 |
| Fan-out/Fan-in | 多个子 agent 并行，再聚合 | 多分析师并列、多因子 |

三者都可以用 MAF 的 `Workflow`（顺序/交接/群聊 + `as_agent()`）或 `Harness Agent`（规划/todo + 一次性审批）来实现内部编排。

## 9. 与两个底座的衔接

- **MASim 侧**：复合 agent 放在 `PlayerPersona`（Actor）内部；`children()` 由 persona 创建并托管，仍满足“Persona owns Player，Player 对 Simulator 隐藏”。
- **MAF 侧**：复合引擎内部用 MAF `Workflow` / `Harness`；对外用 `Workflow.as_agent()` 映射到 `AgentRuntime`；子 agent 若在远端，用 `A2AAgent` 包装。

## 10. 一个贯穿性例子（基金公司）

```text
FundCompanyAgent（复合，LLM supervisor）
  ├─ MacroAnalyst（RAG，异步）
  ├─ FundamentalAnalyst（RAG，异步）
  ├─ RiskManager（规则，同步）
  ├─ ExecutionTrader（规则，同步）
  └─ ExternalAlpha（远端 A2A，跨语言）

decide() 流程：
  supervisor 规划 → 前四个本地子 agent 并行/串行 → aggregate（LLM 摘要）
  → 父输出“仓位意图” → ExecutionTrader 执行 → on_fill 记账
```

## 11. 尚待确认

1. 第一版先实现哪三个组织模式？（建议先 Pipeline + Fan-out/Fan-in，supervisor 后补。）
2. 聚合默认实现先给“统计聚合”还是“统计 + LLM 摘要”两个？（建议两个都给，场景可选。）
3. 复合 agent 是否允许“子 agent 又是远端 A2A 服务”先不做，只留接口？（建议留接口，Phase 2 再打通。）
