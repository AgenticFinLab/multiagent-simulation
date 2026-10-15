# 06 · 编排范式（复合 agent 内部如何组织子 agent）

> 核心问题：一个复合 agent 内部的多个子 agent 怎么组织？这些范式是 `CompositeOrchestrator` 的实现素材。

## 1. 五种范式速览

| 范式 | 系统 | 协作原语 | 适合 |
|------|------|----------|------|
| SOP 流水线 | MetaGPT | 消息总线 + SOP 角色 | 可预测流水线 |
| 对话链 | ChatDev | ChatChain（两两对话） | 链式任务、省 token |
| 交接 | OpenAI Agents SDK/Swarm | handoff | 控制权移交 |
| 模块化环境 | AgentVerse | 环境/描述器/顺序 | 环境类实验 |
| 自动生成团队 | AutoAgents | Drafting→Execution | 动态团队 |

## 2. 各范式要点

### MetaGPT（Code = SOP(Team)）
- 把“软件公司”装进框架：产品经理/架构师/项目经理/工程师按 SOP 协作；一行需求 → PRD/设计/任务/代码仓库。
- 启示：SOP 让团队协作可复用、可预期。

### ChatDev（ChatChain）
- 每个节点是**两个角色对话**（CEO↔CTO、程序员↔测试），链式推进：设计→编码→测试→文档。
- 启示：两两对话比群聊更省 token、更可控。

### OpenAI Agents SDK / Swarm（handoff）
- 把多 agent 编排蒸馏为 **handoff（交接）+ routines（例程）**；handoff 实现为“特殊工具调用”。
- 启示：handoff 是“一个子 agent 交给另一个子 agent”的最小原语。

### AgentVerse（模块化环境）
- 环境、描述器、顺序（random/sequential/concurrent）、agent、记忆五类模块可自定义。
- 启示：“顺序可配置”与“concurrent 每轮全体行动”正是模拟器的核心。

### AutoAgents（自动生成）
- Drafting（起草 agent 团队与计划）→ Execution（执行）。
- 启示：可按需生成 agent 团队（规模下需节流）。

## 3. 通用结论

- 这些是“复合 agent 内部如何组织子 agent”的现成素材，**都不解决“世界推进 + 大规模”**。
- 它们应作为 `CompositeOrchestrator` 的实现候选，而不是整体架构。

## 4. 落到平台契约

- `→ masim/platform/composite/base.py`：`CompositeOrchestrator.run()` 第一版做最简顺序编排 + Fan-out/Fan-in（D10）。
- `→ masim/platform/composite/base.py`：`Aggregator.aggregate()` 先做统计聚合 + LLM 摘要聚合（D10）。
- handoff/SOP 等更复杂范式，后续作为 `CompositeOrchestrator` 的不同实现，或复用 MAF Workflow/Harness。
