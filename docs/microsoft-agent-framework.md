# Microsoft Agent Framework（MAF）设计与结构解读

> 面向对象：想理解微软新一代 Agent 框架“整体在做什么、怎么设计、结构如何、强调什么”，尤其关注**多服务器 / 多 Server**能力。
> 参考资料：[microsoft/agent-framework](https://github.com/microsoft/agent-framework)、[MS Learn 文档](https://learn.microsoft.com/en-us/agent-framework/)、DeepWiki 对该仓库的解读。

## 0. 一句话定位

Microsoft Agent Framework（MAF）是一个**开源、多语言（.NET / Python，Go 预览）的通用 Agent 与多智能体工作流框架**，定位是“把 Agent 从原型做到生产”。它是 Semantic Kernel 与 AutoGen 两条线的融合与继任者（同一批工程团队），统一了 SK 的“内核/编排”与 AutoGen 的“多智能体协作”经验。

README 的官方定义：

> "an open, multi-language framework for building **production-grade AI agents and multi-agent workflows** in **.NET and Python**."

它回答的核心问题不是“怎么写一个能聊天的 Agent”，而是：

- 如何用**一致的 API** 在不同模型供应商之间切换；
- 如何把单个 Agent 组装成**有显式执行路径**的多 Agent 系统（图、分支、并发、交接、群聊）；
- 如何让这些 Agent 系统具备**持久化、可重启、可观测、可治理、人在环**等生产属性；
- 如何**部署成网络服务**，并让不同服务之间通过标准协议互操作（A2A / MCP / AG-UI / OpenAI Responses）。

## 1. 与当前项目（MASim）的对照背景

先给一个快速对照，避免把两个“多智能体框架”混为一谈：

| 维度 | MASim（本仓库） | Microsoft Agent Framework |
|------|----------------|---------------------------|
| 目的 | 金融市场/群体行为的**仿真实验平台**与场景研究 | 通用**生产级 Agent 编排与应用框架** |
| 执行模型 | Ray Actor + 拓扑分层逐轮 `perceive→decide→act` | Agent 会话 + **图工作流**（superstep 收敛） |
| 多 Agent 关系 | 共享市场 + 通信/代理路由 | 图节点/边 + A2A/MCP 协议互操作 |
| 持久化 | 逐轮 Storage / 实验产物包 | Session store、Checkpoint、time-travel |
| “多服务器”含义 | Ray 分布式计算集群 | 多个自托管服务 / Foundry 托管 / 协议级互操作 |
| 语言 | Python | .NET / Python / Go |

一句话：**MASim 偏向“领域仿真 + 分布式计算”，MAF 偏向“生产 Agent 工程 + 标准协议”。** MAF 的价值在于把“单 Agent → 多 Agent → 网络化服务 → 可运维”这条链路做完整。

---

## 2. 总体结构：四大领域 + 五个基础构建块

MS Learn 的 Overview 把 MAF 归纳为**四个 primary areas**（主能力域）：

| 领域 | 职责 |
|------|------|
| **Agents** | 单 Agent：用 LLM 处理输入、调用工具和 MCP server、产出响应 |
| **Harness Agent** | 一个“有观点、电池全带好”的 Agent，面向长程多步任务 |
| **Workflows** | 函数式 + 图式工作流，用显式执行路径连接 Agent 与函数 |
| **Integrations** | 模型供应商、托管（Foundry）、协议、生态（GitHub Copilot SDK 等） |

在四大领域之下，是**五个基础构建块**（foundation building blocks）：

1. **Model clients（模型客户端）**：统一封装 Chat Completions 与 Responses 两条协议路径，上层 API 一致；
2. **Agent session（会话状态）**：承载多轮对话上下文与 Agent 运行态；
3. **Context providers（上下文提供者）**：即“记忆/上下文”来源，如 `ChatHistoryProvider` 与 `AIContextProviders`；
4. **Middleware（中间件）**：拦截 Agent 的动作（请求/响应、异常处理、自定义管道）；
5. **MCP clients（工具/集成客户端）**：连接外部 MCP 工具服务器。

```
                 ┌─────────────────────────────────────────────┐
                 │           四大领域（上层能力）               │
                 │  Agents · Harness Agent · Workflows · Integrations │
                 └───────────────┬─────────────────────────────┘
                                 │ 建立在
                 ┌───────────────▼─────────────────────────────┐
                 │            五个基础构建块                     │
                 │ model clients · session · context providers  │
                 │      middleware · MCP clients                 │
                 └─────────────────────────────────────────────┘
```

![Microsoft Agent Framework 总体架构与执行 Pipeline](diagrams/maf-architecture.png)

---

## 3. Agent 层：统一抽象与管道

### 3.1 统一入口

无论底层走哪个模型供应商，上层调用形态保持一致：

- Python：`Agent` 基类，`await agent.run(...)` / `agent.run_stream(...)`；
- .NET：`AIAgent` 基类，`agent.RunAsync(...)`；常见的 `ChatClientAgent` 由其派生。

“换协议不换上层代码”是 MAF 的关键设计目标。底层可以走 Chat Completions（兼容性最好），也可以走 OpenAI Responses（服务端托管上下文、`previous_response_id` 续接），还可以是 Anthropic Messages API 等。

### 3.2 Agent 管道分层（Pipeline）

从 MS Learn 的 “Agent Pipeline Architecture” 看，一次 Agent 调用大致经过这些层：

```
调用方
  -> Agent middleware（.Use() 装饰器，请求/响应/异常拦截）
  -> Context layer（ChatHistoryProvider + AIContextProviders，装配记忆与上下文）
  -> chat client call（真正调模型）
  -> AgentTelemetryLayer（OpenTelemetry span/event/metric）
```

- **Middleware**：类似 Web 框架的中间件思想，可做日志、限流、缓存、自定义预处理；
- **Context providers**：把对话历史与外部上下文（检索、用户画像、工具结果）注入到每一次调用；
- **Telemetry**：内置 OpenTelemetry，产出分布式 trace、事件与指标，便于生产排障。

### 3.3 多供应商能力

MAF 支持 OpenAI、Azure OpenAI、Microsoft Foundry、Anthropic、Ollama、Amazon Bedrock、Google Gemini、Mistral、GitHub Copilot 等，持续增加。这是“架构随需求演进、不因换供应商而大改”的关键。

### 3.4 Harness Agent

Harness Agent 是“自带一套方法论”的 Agent，面向**长程、多步**任务，开箱自带：

- 规划与 todo 跟踪（planning / todo tracking）；
- 上下文压缩（context compaction）；
- 文件访问与记忆（file access / memory）；
- “不再询问”的工具审批（don't-ask-again tool approval）；
- 可观测性。

它的定位：普通 `Agent` 是无约束的“模型 + 工具 + 会话”，而 Harness Agent 是“告诉你该怎么组织长任务”的有观点的实现。

---

## 4. Workflow 层：图编排与执行语义

### 4.1 图式构建

- `WorkflowBuilder`（构建器）声明节点（Agent / Function）与有向边；
- 执行器三类：`AgentExecutor`（跑 Agent）、`WorkflowExecutor`（嵌套子工作流）、`FunctionExecutor`（跑函数）；
- 支持 `FanOutEdgeGroup` 做**并行扇出**（一条边分叉到多个节点同时跑）。

### 4.2 执行语义：类似 Pregel 的 superstep

工作流按 **superstep（超步）** 收敛执行：一轮一轮推进，直到没有更多需要执行的节点/消息，工作流才结束。这种“图上消息传递 + 收敛”的模型天然支持：

- 顺序（sequential）、并发（concurrent）、交接（handoff）、群聊/协作（group chat / collaboration）等编排模式；
- `magentic` 工作流（把函数/Agent 用简洁方式组合）。

### 4.3 生产特性

- **Checkpointing（`CheckpointStorage`）**：保存中间状态，支持暂停/恢复、从失败点重跑；
- **Streaming（流式）**：逐 token / 逐更新地流式输出；
- **Human-in-the-loop**：`ctx.request_info()` 让工作流暂停进入 `IDLE_WITH_PENDING_REQUESTS`，等外部（人）补信息后继续；
- **Time-travel**：回到历史 checkpoint 重放；
- **组合**：`Workflow.as_agent()` 把一个工作流包装成 Agent，于是“工作流”可以出现在任何期望 Agent 的位置（可嵌套、可当单点复用）。

```
  WorkflowBuilder
     ├─ AgentExecutor   (node: Agent)
     ├─ FunctionExecutor(node: 函数)
     └─ WorkflowExecutor(node: 子工作流, 可嵌套)

  执行：superstep 迭代 -> 收敛
  运行时能力：checkpoint / streaming / HITL / time-travel / as_agent()
```

---

## 5. 托管（Hosting）与集成：MAF 的“服务器观”

### 5.1 核心设计原则：框架不是 HTTP 服务器

MAF 一个很关键的设计立场是：

> 托管辅助（hosting helpers）**不是** HTTP 服务器，也不是协议注册中心。

**应用自己拥有**：路由、认证/授权、请求策略、存储、扩容（scaling）。
**框架提供**：把协议数据转换成 Agent 操作、可选地管理执行状态（session / state）。

这意味着 MAF **不强绑定** FastAPI / ASP.NET Core / Django / Flask / Azure Functions 中的某一个，而是“辅助优先（helper-first）”，让你放进自己的 Web 框架里。

### 5.2 .NET 托管契约

- `AddAIAgent(...)` / `AddWorkflow(...)`：向依赖注入容器注册 Agent / Workflow；
- `IHostedAgentBuilder`：构建被托管的 Agent；
- `AgentSessionStore`：可选启用**持久会话**；
- `IsolationKeyScopedAgentSessionStore`：按隔离键（租户/用户）隔离会话，配合 `AgentIsolationKeyProvider`；基于声明的隔离可用 `UseClaimsBasedAgentIsolation`；
- ASP.NET Core minimal API 端点：如 `MapOpenAIResponses(...)` 直接暴露 OpenAI Responses 协议端点。

### 5.3 Python 托管契约

Python 是“helper-first”：

- `AgentState` + `SessionStore`：解析 Agent 与其会话存储；
- `WorkflowState`：解析 Workflow 实例 / 工厂 / builder；
- 协议包各自独立：
  - `agent-framework-hosting-responses`（OpenAI Responses）
  - `agent-framework-hosting-mcp`（MCP）
  - `agent-framework-hosting-telegram`（Telegram）
  - `agent-framework-hosting-a2a`（A2A）

这些包把不同协议流量“翻译”成 Agent Framework 操作，由应用决定用户身份、会话与存储。

### 5.4 Foundry Hosted Agents（托管）

只需约 2 行代码即可把 Agent 部署到 Foundry 托管的基础设施：

- `ResponsesHostServer` + Responses API 协议；
- checkpoint / 状态持久化；
- SSE 流式输出；
- 通过 Azure CLI / azd 部署。

---

## 6. 多服务器 / 多 Server（重点章节）

MAF 里的“多服务器”不是指一个内置的分布式运行时（像 MASim 用 Ray 那样强制多机），而是**三个层面的叠加**：协议互操作、自托管服务化、托管平台。

### 6.1 A2A：Agent 与 Agent 之间的网络协议（最核心）

A2A（Agent-to-Agent）是让不同语言、不同框架、不同进程/服务器上的 Agent 互相调用的标准协议。MAF 有专门包：

- Python：`agent-framework-a2a`
- .NET：`Microsoft.Agents.AI.A2A`

关键概念：

| 概念 | 说明 |
|------|------|
| **AgentCard** | Agent 的“名片/服务描述”，对外声明自己是谁、能做什么、如何调用 |
| **调用方式** | 通过 HTTP / JSON-RPC 调用远程 Agent |
| **任务模型** | 基于 task 的异步执行，有终止状态 `TASK_STATE_COMPLETED` / `TASK_STATE_FAILED` |
| **continuation token** | 长任务跨请求续接的令牌 |
| **流式** | 支持 streaming 与 non-streaming 两种 |

两侧实现：

- **服务端（把本地 Agent 暴露成 A2A 服务）**：`A2AExecutor`（Python）/ `AgentA2AAdapter`（.NET）把本地 Agent 桥接成 A2A 服务，生成 AgentCard，供其他 A2A 客户端访问；`a2a_to_run` 把 A2A Message 转成框架执行参数，`a2a_from_run` 把框架响应与流式更新转成 A2A Part。
- **客户端（把远程 Agent 当本地 Agent 用）**：`A2AAgent` 包装远程 A2A Agent，使其看起来就像一个本地 Agent。

**价值**：Python 服务 ↔ .NET 服务可以互操作；一个团队用 C#、另一个用 Python，各自部署为独立服务，通过 A2A 调用彼此——这就是最直接的“多服务器”形态。

### 6.2 MCP：Agent 调用多个工具服务器

MCP（Model Context Protocol）让 Agent 调用外部工具：

- Agent 可以声明并调用 **多个 MCP servers**；
- 模型可在不同远程工具集之间选择（如托管 code interpreter、file search、web search）；
- Foundry 也可以托管 MCP server。

这与 A2A 的分工：**A2A = Agent 调 Agent；MCP = Agent 调工具。** 两者都是“多服务器”生态里可组合的协议。

### 6.3 自托管：每个 Agent / Workflow 都是独立服务

因为 MAF 的托管层是“helper-first”，你可以把每个 Agent 或 Workflow 部署成自己的 server / container / service：

- 一个 host（主机）可以同时暴露多种协议：**OpenAI Responses + A2A + AG-UI** 同时存在；
- 多个自托管 server 之间通过 A2A 互操作；
- 会话用 `SessionStore` 持久化，租户/用户用 isolation key 隔离。

这本质上是把“单体 Agent 应用”拆成“一组可独立部署、可扩容、可治理的微服务”，每个服务可独立选择语言与 Web 框架。

### 6.4 多服务器拓扑：没有内置“网关”，但可组合

一个重要事实：**MAF 没有一个内置的统一 Gateway 类。** 社区/样例通常在上层加一个 **API Gateway + 路由 Agent（router agent）**，由路由 Agent 根据请求把流量分发到不同的后端 Agent 服务。

因此 MAF 的多服务器 = **托管灵活性 + 协议互操作（A2A/MCP/AG-UI）**，而不是一个强制性的分布式运行时。与之相对，MASim 用 Ray actor 做分布式计算；二者“多 server”的语义不同。

```
                        ┌──────────────────────┐
       客户端/前端 ─────▶│  API Gateway + 路由    │
                        └──────────┬───────────┘
                                   │ 按意图分发
          ┌────────────────────────┼────────────────────────┐
          ▼                        ▼                        ▼
  ┌──────────────┐        ┌──────────────┐        ┌──────────────┐
  │ Server A     │  A2A   │ Server B     │  A2A   │ Server C     │
  │ (Python Agent)│◀─────▶│ (.NET Agent) │◀─────▶│ (Workflow)    │
  └──────┬───────┘        └──────┬───────┘        └──────┬───────┘
         │ MCP                   │ MCP                   │ MCP
         ▼                       ▼                       ▼
    工具服务器              工具服务器              工具服务器
```

![Microsoft Agent Framework 多服务器 Pipeline](diagrams/maf-multiserver-pipeline.png)

### 6.5 会话隔离与多租户

生产级“多服务器”离不开租户/用户隔离：

- `.NET`：`IsolationKeyScopedAgentSessionStore` 按隔离键作用域化会话；`AgentIsolationKeyProvider` 提供隔离键；`UseClaimsBasedAgentIsolation` 基于 token 声明推导隔离键；
- `Foundry`：`FoundrySessionStore`（Python）/ `HostedSessionIsolationKeyProvider`（.NET）从请求上下文提取会话标识。

这保证同一个 Agent 服务被多个用户/租户同时调用时，会话状态不会串。

---

## 7. 设计着重点小结

1. **Production-grade 优先**：持久化、可重启、可观测、可治理、人在环是默认考量，而非事后补丁；
2. **API 一致性 + 供应商灵活性**：Chat Completions / Responses / Anthropic 等协议在统一抽象之下，换供应商不重写上层；
3. **显式编排**：用图工作流表达顺序/并发/交接/群聊，执行路径可读、可 checkpoint、可重放；
4. **辅助优先的托管**：框架不抢 Web 框架的活，应用拥有路由、鉴权、存储与扩容，框架负责协议翻译与状态管理；
5. **标准协议互操作**：A2A（Agent 调 Agent）、MCP（Agent 调工具）、AG-UI / OpenAI Responses（对外暴露），让“多服务器”以协议而非强制运行时实现；
6. **多语言一致**：.NET / Python 全功能，Go 预览，跨语言通过 A2A 互操作；
7. **生态与治理**：OpenTelemetry、Declarative Agents（YAML 声明式定义）、Agent Skills、DevUI、AF Labs（实验特性）。

---

## 8. 与 MASim 的对比小结

| 关注点 | MASim | MAF |
|--------|-------|-----|
| 本质 | 领域仿真平台（金融市场） | 通用生产 Agent 框架 |
| 多智能体如何组织 | Ray actor + 拓扑分层 + 通信代理 | 图工作流 + A2A/MCP 协议 |
| 运行/部署 | Ray 集群、逐轮 Storage | 自托管服务 / Foundry 托管 |
| 持久化 | 轮次记录、实验包 | Session store、checkpoint、time-travel |
| 可观测 | 分析产物、指标 | OpenTelemetry 分布式追踪 |
| 强调 | 行为涌现、场景复现、市场机制 | 编排、可运维、协议互操作、治理 |

**一句话总结**：如果 MASim 是在“用 Ray 跑大规模经济仿真”，那么 MAF 是在“用标准协议与图编排把 LLM Agent 系统做成可部署、可互操作、可治理的生产服务”。两者在多智能体“组织与协作”的思路上有交集，但**MAF 的“多服务器”重点在协议级互操作（A2A / MCP / AG-UI）+ 服务化托管 + 会话隔离**，而不是内置分布式计算运行时。

---

## 附：关键参考链接

- 仓库：[microsoft/agent-framework](https://github.com/microsoft/agent-framework)
- Overview：[MS Learn — Agent Framework Overview](https://learn.microsoft.com/en-us/agent-framework/overview/)
- 自托管：[Self-host Agent Framework applications](https://learn.microsoft.com/en-us/agent-framework/hosting/self-hosting/)
- A2A 自托管：[Self-host A2A agents](https://learn.microsoft.com/en-us/agent-framework/hosting/self-hosting/a2a)
- 托管协议（Responses/MCP/Telegram）与 Foundry Hosted Agents：MS Learn hosting 目录
