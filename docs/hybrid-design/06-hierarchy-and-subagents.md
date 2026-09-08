# 06 · 层级组织与 sub-agent

## 1. 为什么必须分层

规模问题（B1/B2）本质是“扁平全连接 + 全量 LLM”不可扩展。分层是同时压缩**决策次数**和**消息条数**的手段：

- **压缩决策次数**：leader 做一次 LLM 决策，成员用规则跟随，把 O(N) 次 LLM 降到 O(组数)。
- **压缩消息条数**：组内 O(k²) + 组间 O(m²)，k、m ≪ N，把 O(N²) 降到 O(N·k + m²)。

## 2. 三种层级模式

### 2.1 supervisor-worker（树形，用于复合 agent 内部）
- 每个内部节点负责规划、分派、汇总、验证；只有叶子真正“干活”。
- 对应 MAF 的 Harness Agent / supervisor 模式。
- 适用：**一个 agent 内部有明确分工**（基金公司 = 经理 + 分析 + 风控 + 交易）。

### 2.2 group + leader（星形，用于大规模同类 agent）
- 把 N 个同类 agent 分成若干组，每组一个 leader 代表组做 LLM 决策/对外通信。
- 成员用规则跟随 leader 的“意图”，降低 LLM 与消息开销。
- 适用：**几万~几十万同类投资者/意见传播者**。

### 2.3 hub / coordinator（星形或扇入扇出，用于市场与信息分发）
- 市场 coordinator 已是 hub（所有交易者扇入）。
- 信息分发 hub（类似 OASIS 的推荐系统）：先聚合内容，再按兴趣路由给订阅者，避免全对全。
- 适用：**新闻、行情、帖子、意见的大规模传播**。

## 3. 复合 agent 的递归语义

```text
AgentRuntime.children() -> [AgentRuntime]   # 可递归
```
- 叶子 = 原子决策单元（Rule 或单次 LLM）。
- 内部 = CompositeEngine（Workflow / Harness / supervisor）。
- 递归终止条件：children 为空，或达到最大深度（配置限制，防止无限嵌套）。
- **对外透明**：市场/消息系统只看到“一个 agent”，不关心它内部有几层。

## 4. 分层带来的新问题（必须一并设计）

1. **聚合失真**：leader 汇总成员时会丢信息 → 设计“聚合摘要 schema”，保留统计量 + 关键离群样本。
2. **因果延迟**：信息从叶子到根再到叶子会延迟 → 明确层级是“逻辑聚合”还是“物理多跳”，并限制跳数。
3. **责任与溯源**：leader 的决策要能追溯到“基于哪些成员的聚合” → 聚合结果带 `(group_id, member_count, summary, outliers, version)`。
4. **负载不均**：热门 leader/hub 成为瓶颈 → leader/hub 可再分片或多副本。
5. **一致性**：leader 决策期间成员状态变化 → 用“决策快照”（leader 基于某一轮次的状态聚合）。

## 5. 层级深度建议

| 规模 | 建议层级 | 说明 |
|------|----------|------|
| 10² | 1 层（扁平 + 复合 agent 内部 1 层） | 保真 |
| 10³ | 2 层（group + leader） | 分组 |
| 10⁵ | 3 层（成员→group leader→区域/角色 hub→市场） | 多级聚合 |

经验法则：**每层聚合比（成员数）控制在 10~100**，避免单点过载，也避免层级过深导致失真与延迟。

## 6. 与 MAF 能力的映射

| 层级模式 | MAF 表达 | 说明 |
|----------|----------|------|
| supervisor-worker | Harness Agent / Workflow（handoff、group chat） | 动态任务分解与验证 |
| group + leader | Workflow 的 FanOut/FanIn + checkpoint | leader 汇总分支 |
| hub | 自定义 Agent（rule）+ 兴趣路由 | MAF 不管大规模路由，由我们内部总线做 |
| 递归复合 | `Workflow.as_agent()` 嵌套 | 工作流可出现在任何 agent 位置 |

## 7. 落地约束（贴合 MASim 现状）

- MASim 已把“市场 coordinator”作为 hub；我们**不改变**四阶段与拓扑语义，只在其上叠加 group leader 与复合 agent。
- group leader 可以在拓扑中作为一个新层级（介于成员与市场之间），由 `topology.yml` 表达，避免硬编码。
- 复合 agent 的 `children()` 在 `PlayerPersona`（Actor）内部创建，仍满足“Persona owns Player，Player 对 Simulator 隐藏”的既有原则。
