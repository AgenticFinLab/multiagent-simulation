# 07 · 通信与协议

## 1. 两层通信模型

- **内部（数据面）**：轻量、高性能、专用消息总线，沿用并扩展 MASim 三层消息模型。
- **外部（互操作面）**：标准协议（A2A / MCP / AG-UI），用于跨语言、跨服务、工具与人的接入。

原则：**内部性能敏感不走外部协议；跨系统一律走标准协议。**

## 2. 内部消息总线：扩展三层模型

MASim 现有 `Info → Message → SimPacket`：

| 层 | 类型 | 职责 |
|----|------|------|
| Player | `Info` | 业务内容 |
| Proxy | `Message` | 加 sender/recipient/时间戳/优先级 |
| Channel | `SimPacket` | 可记录、可传输的编码包 |

混合架构在保留三层模型基础上增加三类“规模化必需”的语义：

1. **聚合消息（AggregateMessage）**：leader 汇总成员信息后只发一条摘要（带统计量 + 离群样本），而非逐条转发。
2. **兴趣路由（Interest Routing）**：消息带 topic/兴趣标签，由 hub 按订阅关系分发，而非全对全广播。
3. **引用/延迟加载（Reference）**：传摘要 + 引用（id/url），接收方按需拉全文，避免大消息刷屏。

## 3. 路由策略（按交互类型）

| 交互 | 路由策略 | 复杂度 |
|------|----------|--------|
| 交易 → 市场 | 扇入到 coordinator（已有） | O(N) |
| 行情/公告 → 全体 | hub 广播，摘要 + 按需拉取 | O(N) 但内容小 |
| 意见/信号传播 | 兴趣订阅 + hub 转发 + 拓扑边 | O(N·k) |
| 组内协作 | group 内部直连 | O(k²) 每 k 小组 |
| 组间协作 | leader ↔ leader / leader ↔ hub | O(m²) |
| 复合 agent 内部 | 本地调用或 Workflow 图 | 进程内 |

## 4. 外部协议桥（借用 MAF）

### 4.1 A2A（agent ↔ agent）
- 把一个内部 agent（尤其复合 agent / group leader）通过 `A2AExecutor` 暴露为**带 AgentCard 的 A2A 服务**。
- 外部/远端 agent 用 `A2AAgent` 包装成内部 `AgentRuntime`，父 agent 无需感知其是远端。
- 用途：
  - 跨语言（Python 世界 ↔ .NET 决策服务）；
  - 跨团队/跨组织复用 alpha 服务、监管服务、外部市场；
  - 把“重决策”外包给独立可扩容的 agent 服务，减轻本地集群负担。

### 4.2 MCP（agent ↔ 工具/知识）
- 工具（代码执行、数据、搜索）、知识库、外部 API 以 MCP server 暴露，agent 声明并调用多个 MCP server，模型按需选择。
- 用途：RAG 检索、行情/新闻数据、回测/风控计算器。

### 4.3 AG-UI（人机）
- 交互式调试、人在环（HITL）、实验监控面板。
- 借用 MAF 的 AG-UI/Responses 托管把某个 agent 暴露给人查看/介入。

## 5. 协议选择的决策表

| 需求 | 选择 |
|------|------|
| 内部 agent 间高频消息 | 内部消息总线（不引入外部协议） |
| 跨语言/跨服务 agent 调用 | A2A |
| agent 调工具/知识/数据 | MCP |
| 人机交互/调试/HITL | AG-UI / Responses |
| 外部系统观察实验 | 只读事件流 + 指标（可复用 AG-UI） |

## 6. 一致性与顺序（结合 B4）

- 内部消息带 `(round, level, sender, seq, clock)`，按拓扑层级屏障保证“Level N 消息先于 Level N+1”。
- 外部 A2A/MCP 调用是异步长延迟：进入“pending 决策”队列，到点仍未返回则按策略**降级或使用缓存/默认值**，不阻塞世界推进。
- 幂等：消息带 seq，重复投递不重复消费（复合 agent 的聚合尤其需要）。

## 7. 与 MASim 现状的衔接

- 保留 `GeneralCommunicationChannel.encode_and_deliver` 与 `build_message_from_info`。
- 在 Proxy 层新增 `AggregateProxy` / `InterestRouter`（可选插件），而不是改动 Channel 核心。
- `topology.yml` 扩展：增加 `group` / `hub` / `interest` 三类关系，仍然由 `TopologyGraph` 计算执行层级。
