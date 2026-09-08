# 08 · 状态、存储与持久化

## 1. 冷/温/热三级状态

| 级 | 存放 | 内容 | 访问延迟 | 生命周期 |
|----|------|------|----------|----------|
| 热 | agent actor 内存 | cash/position、短期记忆、当前观察 | 纳秒~微秒 | 一轮内 |
| 温 | 本地 KV / 文件 / 进程外缓存 | 逐轮记录、HistoryBuffer、聚合摘要 | 毫秒 | 单次实验 |
| 冷 | 对象存储 / 向量库 | 长期记忆、知识、快照、发布包 | 10~100ms | 跨实验持久 |

原则：**越热的越贵越少，越冷的越便宜越多。**

## 2. StateStore 统一接口

```text
save(agent_id, state) / load(agent_id) -> state
append_record(agent_id, round, record)      # 追加逐轮记录
checkpoint(round, level) / restore(round, level)
scope(isolation_key) -> StoreView           # 多租户隔离视图
```

- 所有 agent 通过 StateStore 读写，而不是直接摸文件/对象存储。
- 好处：底层可从“本地文件”平滑换成 Redis/S3/向量库，agent 代码不变。

## 3. 快照与断点续跑（B6）

- **轮级 checkpoint** 为最低粒度：MASim 已有 `detect_resume_round` + `write_resume_checkpoint`，保留并推广到 group/复合 agent。
- **层级快照**（level 级）：对长 LLM 决策多的层级，保存“已完成 level”，重跑只从当前 level 继续。
- **快照一致性**：actor 状态序列化 + 消息队列游标 + 市场订单簿，三者一起快照。
- **恢复语义**：恢复后 `round` 严格对齐；LLM 路径若无法精确复现，用 `prompt_hash + 缓存` 保证同输入同输出。

## 4. 幂等（B6）

- 消息带 `(round, level, sender, seq)`，消费者按 seq 去重。
- 聚合消息带 `(group_id, version)`，重复聚合只生效一次。
- 决策写入带 `(agent_id, round, decision_hash)`，重复写入幂等覆盖。

## 5. 多租户隔离（B8）

- 隔离键 = `run_id / scenario / mechanism / tenant` 的组合（借鉴 MAF `IsolationKeyScopedAgentSessionStore`）。
- 所有 StateStore 视图、消息总线命名空间、LLM 配额按隔离键作用域化。
- 外部 A2A 接入必须绑定鉴权，client 提供的 id 仅作连续性标识，不作授权（MAF 的安全指导）。

## 6. 长期记忆与知识（B3）

- 长期记忆进向量库：只存“影响决策的关键事件/摘要”，用检索替代全量回放（生成式 agent 的 memory-reflection 机制）。
- 复合 agent 不重复存子状态全文，存子状态**摘要 + 引用**，需要时再从子 agent 拉取。
- 知识库（论文/新闻/政策）走 RAG 或 MCP 知识工具，冷存。

## 7. 存储规模估算（用于选型）

假设每 agent 每轮记录 ~200B：

| 规模 | 每轮记录 | 1000 轮 |
|------|----------|---------|
| 10² | 20KB | 20MB |
| 10³ | 200KB | 200MB |
| 10⁵ | 20MB | 20GB |

- 10⁵ × 1000 轮已是 20GB 量级，必须**追加式分区存储 + 压缩 + 列式/parquet 化**，并用 `load_results()` 式接口读取而非全量加载内存。
- 全量决策 I/O 溯源不可行，改为**采样溯源**（关键 agent / 关键轮全量，其余统计）。

## 8. 与 MAF 的衔接

- 用 MAF `SessionStore` 的接口思想做“agent 会话状态”，用 `isolation key` 做多租户。
- 复合 agent 内部若用 MAF Workflow，则其 checkpoint 复用 MAF `CheckpointStorage`；对外再由 StateStore 包一层，统一到同一生命周期。
