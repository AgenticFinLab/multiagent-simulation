# 05 · 记忆 - 反思 - 规划（agent 行为学基础）

> 核心问题：几十万 agent 的记忆怎么存、怎么用，才能“像人”又不爆炸？

## 1. Generative Agents（Park et al., UIST 2023）

- 三件套：
  1. **记忆流（Memory Stream）**：一条不断增长的观察记录列表。
  2. **检索（Retrieval）**：按 **recency（新近）、importance（重要性）、relevance（相关性）** 三信号加权取回。
  3. **反思（Reflection）**：当“足够多的重要事情发生”时，把记忆泛化为高层洞察（**重要性预算触发**，无监督）。
  4. **规划（Planning）**：递归任务分解（天 → 小时 → 分钟），每层计划也存入记忆流，持续再规划。
- 关键点：观察、反思、计划**同处一个记忆流**，检索时相互竞争。

### 对实现的启示
- `→ masim/platform/state/base.py`：`StateStore` 需要支持“冷/温/热”与检索；长期记忆只存关键事件 + 摘要，不全量回放。
- `→ masim/platform/agent/base.py`：`observe()` 把观察写入记忆；`decide()` 从记忆检索。

## 2. Generative Agent Simulations of 1,000 People（Park et al., 2024）

- 核心：**访谈校准 + 专家反思**——AI 访谈者半结构化访谈 + 动态追问；专家反思模块从 4 个领域专家视角合成访谈；**全文注入**（非摘要）；思维链。
- 结论：个体级访谈校准能显著提升行为对齐，但**10⁵ 规模不可行**。

### 对实现的启示
- L1（几十）可用“访谈校准”；L3（几十万）退化为**统计校准（分布对齐）+ 模板 + 参数化 persona**。
- 这决定 `Config/ScenarioLoader` 的 persona 生成接口要支持“逐人（L1）/ 模板批量（L3）”两种。

## 3. MemGPT / Letta（分层记忆 + 虚拟上下文）

- 核心：把上下文窗口当 RAM 管理（**Virtual Context**）。
- 三层记忆：Core Memory（常驻，2–4K）、Working Memory（分页）、Archival Memory（归档检索）。
- 操作：**Paging（换页）、Summarization（压缩）、Retrieval（检索）、Eviction（淘汰）**。

### 对实现的启示
- 这正是平台“冷/温/热三级状态”的 agent 侧实现：核心常驻、历史归档、满则压缩/淘汰。
- `→ masim/platform/state/base.py` 的三级语义可直接借鉴；`KnowledgeStore` 做向量检索。

## 4. 规模化后的记忆结论

| 规模 | 记忆策略 |
|------|----------|
| 10² | 记忆流 + 反思 + 规划（Park 完整版） |
| 10³ | 分层记忆 + 反思节流 |
| 10⁵ | 压缩 + 检索 + 统计校准，反思只对少数 agent |
