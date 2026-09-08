# 05 · Agent 分类学与混合决策引擎

## 1. 统一 Agent 抽象（AgentRuntime）

所有 agent 实现同一接口，差异只在 `decide()` 由哪个引擎执行。

```text
AgentRuntime
  ├─ observe(observation, prev_result)
  ├─ decide()  ────── 分派到某个 DecisionEngine ──────► Decision
  ├─ act(decision) → action
  ├─ on_fill(...)                     # 成交后钩子（仅交易型 agent 需要）
  └─ children() -> [AgentRuntime]     # 复合 agent 的子 agent
```

与 MASim 的契约保持一致：**框架统一做 `_apply_fill_and_emit_action`（校验 bid>0、clip 流动性、更新 cash/position），archetype 只覆盖 `on_fill`，禁止 override `act/decide`。** 混合架构保留这条边界，只是把 `decide` 的实现交给引擎层。

## 2. 五类 agent 的引擎映射

| Agent 形态 | DecisionEngine | decide 的实现 | 子 agent |
|-----------|----------------|---------------|----------|
| 纯代码/规则 | RuleEngine | 确定性函数/状态机 | 无 |
| LLM | LLMEngine | prompt + LLM 调用 | 无 |
| 混合 RuleLLM | LLMEngine + RuleEngine 约束 | 规则先约束输出 schema，LLM 在契约内填值 | 无 |
| RAG | RAGEngine | 检索 → LLM → 决策 | 无 |
| 复合 | CompositeEngine | 编排 children + 汇总 | 有（可递归） |

## 3. RuleEngine

- 同步、微秒级、确定性、可复现。
- 覆盖：做市、套利、噪声交易、技术指标策略、市场 coordinator 撮合。
- 接口：`decide(context) -> decision_payload`，纯函数优先（便于缓存与并行）。

## 4. LLMEngine

- 使用 MAF 模型客户端统一供应商（Chat Completions / Responses），一套代码切 OpenAI/Azure/Foundry/Anthropic/Ollama 等。
- 在引擎层叠加四件事（详见 `09`）：
  1. 批处理与异步预取；
  2. prompt/语义/结果三级缓存；
  3. 降级链（LLM→RuleLLM→Rule）；
  4. token 配额与记账。
- 决策记录：`model/version/prompt_hash/temperature/engine`，保证可复算。

## 5. RAGEngine

- 检索（MASim `KnowledgeManager` 或 MCP 知识工具）→ 注入上下文 → LLM 决策。
- 检索缓存与“引用式上下文”（只传文档 id + 摘要，避免重复塞全文）是规模化关键。

## 6. CompositeEngine（复合 agent 的决策器）

这是混合架构最关键的增量。一个复合 agent 的 `decide()` 由内部编排完成：

- 内部可以用 **MAF Workflow**（图：顺序/并发/交接/群聊 + checkpoint + HITL + `as_agent()`）；
- 或用 **MAF Harness Agent**（规划/todo、上下文压缩、文件/记忆、一次性工具审批）作为“子 agent 的经理”；
- 或用 **supervisor-worker**（supervisor 拆解任务、分派 worker、汇总验证）。

三个层次的选择：

| 复杂度 | 推荐内部结构 | 例子 |
|--------|--------------|------|
| 低 | 顺序函数链（本地子函数） | 简单策略 + 风控检查 |
| 中 | MAF Workflow（有向图 + checkpoint） | 分析师→风控→组合经理 |
| 高 | Harness / supervisor-worker（动态规划） | 基金公司 = 多个团队、动态任务 |

## 7. 子 agent 的运行位置（部署策略）

一个复合 agent 的子 agent 可以放在三处，策略按“热/重/便宜”分：

| 位置 | 适合 | 代价 |
|------|------|------|
| 本地函数/协程 | 便宜、高频、无状态 | 无隔离、占用父 actor CPU |
| 本地 Ray actor | 有状态、需并行 | 调度开销 |
| 远端 A2A 服务 | 重、跨语言、跨团队复用 | 网络 + 协议开销 |

> 关键：**子 agent 对外也是一个 `AgentRuntime`**，所以无论放哪，父 agent 的编排逻辑不变——这就是“整齐、标准”的体现。

## 8. 一个贯穿性例子：基金公司 = 复合 agent

```text
FundCompanyAgent（复合，LLM manager）
  ├─ MacroAnalyst（RAG：读新闻/政策）
  ├─ FundamentalAnalyst（RAG：读财报/研报）
  ├─ RiskManager（Rule：仓位/回撤约束，同步）
  ├─ ExecutionTrader（Rule：TWAP/VWAP 拆单，同步）
  └─ (可选) ExternalSignalAgent（远端 A2A：外部 alpha 服务）
```
- 前四个子 agent 在本地，`ExecutionTrader` 是同步规则、`RiskManager` 同步规则；`Macro/Fundamental` 走 RAG（异步）。
- `ExternalSignalAgent` 通过 A2A 接外部，跨语言/跨服务。
- 父 agent 用 MAF Workflow 编排，`Workflow.as_agent()` 对外表现为一个普通 agent，可被市场当成一个投资者。

## 9. 引擎选择矩阵（规模 → 配比）

| 规模 | Rule 占比 | LLM 占比 | RAG/复合 | 说明 |
|------|-----------|----------|----------|------|
| L1 几十 | 低 | 高 | 高 | 保真优先 |
| L2 几千 | 中 | 中（活跃子集） | 中（少量复合代表） | 分组 + 抽样 |
| L3 几十万 | 极高 | 极低（关键/抽样） | 低（高层 leader） | 规则/行为为主 |

> 这个矩阵不是写死，而是“规模策略配置”的默认起点，可由控制面按场景目标调整。
