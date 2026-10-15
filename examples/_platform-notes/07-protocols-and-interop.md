# 07 · 协议与互操作

> 核心问题：内部高频通信与外部跨系统/工具/人，分别用什么？为什么内部不走标准协议？

## 1. 协议全景

| 协议 | 定位 | 传输 | 状态 |
|------|------|------|------|
| MCP | 模型 ↔ 工具/数据 | JSON-RPC / Streamable HTTP | 采用最广 |
| A2A | agent ↔ agent 任务协作 | JSON-RPC over HTTP | 跨语言 |
| AG-UI | agent ↔ 前端/人 | HTTP + SSE | 增长 |
| ANP | 去中心化 agent 网络（DID） | Web 原生 | 早期 |
| ACP | agent 云平台互操作 | — | 早期 |

## 2. 分工一句话

- **MCP** 让 agent 有“执行能力”（连工具/数据/业务系统）。
- **A2A** 让 agent 有“协作能力”（发现并委托其他 agent）。
- **AG-UI** 让 agent 有“可交互性”（给人看/介入）。
- **ANP/ACP**：愿景是 Agent 公网/云，带身份与鉴权——我们暂不引入。

## 3. 内部 vs 外部的边界（D1）

```text
内部（同集群/同进程高频）→ MessageBus（Info→Message→SimPacket + RoutePolicy）
外部（跨语言/跨系统/工具/人）→ A2A / MCP / AG-UI
```

- 内部不走标准协议：性能敏感，协议序列化/网络是额外开销。
- 外部必须走标准协议：可互操作、可替换、生态成熟。

## 4. 安全（必须强制，D10）

- A2A 的 **AgentCard 只做能力发现，不做授权**。
- 多用户宿主必须**绑定鉴权**；客户端提供的 id 仅作“连续性标识”，不是授权令牌。
- `ProtocolBridge` 的契约里把这一点显式声明为强制项。

## 5. 落到平台契约

- `→ masim/platform/message/base.py`：内部 MessageBus（第一版最简，聚合/兴趣路由后续补）。
- `ProtocolBridge` 不写 base.py（复用 MAF 的薄适配层），但需一个“内部 agent ↔ 外部协议”的适配约定：
  - 内部 agent → A2A 服务（带 AgentCard）
  - 外部 A2A agent → 包成 AgentRuntime
  - MCP server → 工具注册
