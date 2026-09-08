# 运行框架与工程机制：为什么采用这条路线

[证据入口](README.md) · [模拟器与建模方法](01-simulation-systems.md)

## 1. MAF：行为与局部活动的运行基础

官方文档提供 Agent、会话、工具、中间件、Workflow、外部请求与 checkpoint 等构件。对本方案最关键的是：局部执行可以返回请求并保存位置，之后以响应继续。[MAF 请求响应](https://learn.microsoft.com/en-us/agent-framework/workflows/human-in-the-loop)、[checkpoint](https://learn.microsoft.com/en-us/agent-framework/workflows/checkpoints)

**选择理由：** 复杂行为和活动已经需要图、工具、模型与接续，采用 MAF 可以集中复用这些构件。函数行为继续走统一合同，通用模型类型不依赖 MAF。

**需要新增：** 模拟身份与行为实例管理、当前可见输入、请求去重，以及连接模拟后果和全局提交的 WorkflowBridge。

嵌套工作流和 Workflow-as-Agent 为内部角色组合提供入口；参考源码将子工作流状态与待请求映射纳入父流程检查点。采用时为不同实例创建隔离对象，顶层 checkpoint 统一关联局部状态。[MAF Workflow-as-Agent](https://learn.microsoft.com/en-us/agent-framework/workflows/as-agents)、[嵌套执行器源码](https://github.com/microsoft/agent-framework/blob/4507512f95effaae4518d658e86e9afc0ccb4514/python/packages/core/agent_framework/_workflows/_workflow_executor.py)

**证据限制：** 嵌套执行不自动建立角色长期记忆、世界权限或动态成员协议。恢复还需完整性检查与新观察注入；这些适配及联合恢复仍需新系统集成验证。

## 2. MASim：迁移资产与实际改造点

MASim 已有主体、配置、拓扑、通信分层、Ray 执行与记录入口。通用执行使用 execute、collect、dispatch、record 的分阶段组织。[GeneralSimulator](../../../masim/simulator/general.py)

**选择理由：** 迁移这些职责清楚的资产和有效测试，能延续已有工程经验。

**需要改造：** 主体状态与每主体 Ray Persona 的绑定、固定轮次接续、领域行为和副作用之间的耦合。当前通用 resume 说明 custom_state 从配置重建，不能据轮数定位直接宣称完整恢复。

**采用位置：** [迁移表与工程结构](../11-migration-and-engineering.md)。迁移时逐项记录保留的行为、适配内容与测试结果。

## 3. Matrix：让执行规模成为独立问题

Meta 的 Matrix 面向多 Agent 合成数据生成，在 Ray 上提供推理与 peer-to-peer 编排；官方项目报告该负载下的吞吐收益。[Matrix 官方仓库](https://github.com/facebookresearch/matrix)

**本稿推论：** 模型请求与多 Agent 工作量值得作为单独执行层管理，应测量队列、worker 利用率和模型服务瓶颈，避免所有业务职责堆在一个协调循环中。

**采用位置：** [共享执行与配额](../08-execution-and-scaling.md)。

**适用边界：** 独立生成工作流与共享模拟世界的冲突条件不同。共享世界仍需明确提交协调，其执行吞吐应在相应负载下独立测量。

## 4. LangGraph：局部进度与长期状态分别管理

LangGraph 官方持久化说明区分 thread 范围的 checkpoint 与跨 thread 的长期 store。[LangGraph Persistence](https://docs.langchain.com/oss/python/langgraph/persistence)

**本稿推论：** 行为实例的 checkpoint 和局部会话，与主体及内部角色的长期记忆应有清楚归属。恢复局部工作流时，还要核对它与共享世界的版本关系。

**采用位置：** [记忆归属](../04-agents-and-memory.md)、[联合恢复](../09-state-and-recovery.md)。

**适用边界：** 本方案借鉴这一职责区分，并以 MAF 为行为运行时；全局模拟提交通过独立的状态协议实现。

## 5. TradingAgents：复杂主体可以由内部角色组合

官方项目将分析、研究、交易和风险管理等角色组合成决策流程。[TradingAgents 官方仓库](https://github.com/TauricResearch/TradingAgents)

**本稿推论：** 复合主体可以使用持久内部角色分工，由 MAF Workflow 组织局部计算。长期角色经验与本次会话分别保存，对外行动归于父主体。

**采用位置：** [内部角色、组织与活动](../04-agents-and-memory.md)。

**适用边界：** 本方案的 SubAgent 使用父主体的对外身份。需要独立世界权限与生命周期的成员建模为独立 Actor。金融角色不成为通用框架的固定类，角色协作也不直接证明主体规模或实证有效性。

## 6. Ray 与 PostgreSQL：执行和生效的基础构件

Ray 提供远程任务与 Actor，异步 Actor 的单事件循环限制需要在 worker 设计中处理。[Ray 异步说明](https://docs.ray.io/en/latest/ray-core/actors/async_api.html)

PostgreSQL 提供事务，用于同时保存状态与后续事件引用。[PostgreSQL 事务说明](https://www.postgresql.org/docs/current/tutorial-transactions.html)

**选择理由：** 分别使用成熟的执行与事务构件，把新增工作集中在任务身份、接续和模拟后果合同。

**适用边界：** Ray 自动重试不能代替效果去重，数据库事务也不自动覆盖外部模型调用或工具副作用。双方需要通过应用层的候选与提交协议连接。

## 7. 形成的工程判断

| 来源经验 | 本稿采用 | 本稿承担的新增工作 |
|---|---|---|
| MAF 局部、嵌套工作流与接续 | 复杂行为、内部协作和活动运行 | 持久角色、当前视图、模拟时间与提交映射 |
| MASim 模拟组织经验 | 主体、环境、通信和 Ray 资产迁移 | 通用组件化、持续活动、完整恢复 |
| Matrix 执行层经验 | 共享 worker、调用治理和负载分解 | 共享世界中的受控生效 |
| LangGraph 状态分工 | 实例会话与主体/角色长期状态分离 | 跨对象版本与恢复一致性 |
| TradingAgents 角色协作 | 内部复合行为 | 内部角色与独立模拟主体的权限区分 |
| Ray / PostgreSQL | 执行资源与事务支撑 | 所有权、有效尝试与重复效果处理 |

这些依据支持明确的职责组合。相对成熟度、实际开发成本和性能收益，最终仍由新系统的实现和验收决定。
