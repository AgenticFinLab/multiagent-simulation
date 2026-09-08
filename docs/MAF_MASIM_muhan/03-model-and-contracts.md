# 03 · 模型装配与接口合同

[返回总览](README.md) · 前一篇：[总体架构](02-architecture.md) · 下一篇：[主体与记忆](04-agents-and-memory.md)

本文定义模块之间的数据边界。以下类型、字段与签名均为拟实现合同，尚不是可调用的 SDK；MAF 和 Ray 对象仅存在于相应适配层。

## 1. 模型由哪些组件组成

| 定义 | 主要内容 | 组合检查 |
|---|---|---|
| ActorDefinition | 角色、属性类型、行为、记忆和主体更新规则 | 行为输入输出、允许字段、身份约束 |
| PopulationDefinition | 主体模板、数量、分布、种子、关系生成器 | 身份唯一、参数分布有效、资源不重复分配 |
| BehaviorDefinition | 函数或 MAF 工厂、提示配置、工具、计算限额 | 工具能力与行为合同兼容 |
| EnvironmentDefinition | 模块、状态范围、操作、信息视图及定时规则 | 字段归属唯一、跨模块操作完整 |
| ActivityDefinition | 流程模板、参与条件、成员规则、等待和结束条件 | 流程版本、身份绑定、反馈处理 |
| Time / Visibility Policy | 激活、延迟、阶段、观察、通信与记忆规则 | 时间合法、接收者规则明确 |

ModelRegistry 将这些定义装配成 `ValidatedSpec`，保存规范化配置、组件版本与摘要。数据文件是可选输入，合成分布和声明假设可以直接初始化模型。

群体生成按 `run_seed + population_id + member_index` 派生稳定身份与随机流，避免并行生成顺序改变初始化结果。生成参数和展开后的初始状态都保存。创建、退出或停用主体采用后续提交的生命周期操作，并清理活动绑定与消息接收规则。

## 2. 长期对象与执行对象

| 类型 | 必要字段 | 含义 |
|---|---|---|
| ActorState | actor_id、definition_version、attributes、memory_refs、relation_refs、status | 主体的持久身份和状态 |
| ActivityState | activity_id、template_version、members、status、continuation_ref、pending_request_ids | 跨模拟时刻持续的交互 |
| SnapshotView | run_id、state_version、coord | 指定版本的只读视图，按需装载 |
| ActorView | actor_id、activity_id?、state_version、visible_fields、inbox、memory、capabilities | 某主体在本次执行可见的信息 |
| ExecutionRequest | run_id、task_id、attempt_id、owner_epoch、coord、read_version、target、views、responses、resume_ref、limits | 一次逻辑激活的具体执行尝试 |
| SegmentResult | task_id、attempt_id、read_version、requests、actor_updates、continuation_ref、disposition、record_refs | 完整片段的候选结果 |
| CommitBatch | commit_id、phase_id、expected_version、selected_attempts、state_changes、events、record_refs | 本阶段准备生效的联合变化 |
| CommitReceipt | commit_id、state_version、coord、event_refs | 确认已经生效的版本及后续事件 |

`target` 标识独立主体或活动；`views` 为参与者分别保存 ActorView。适配器可以持有视图映射，但每次模型调用只接收所绑定主体的视图。ActorView 中的引用访问也须通过身份与版本校验。

`disposition` 表示片段是等待还是完成；执行异常保存为尝试失败，不伪装成正常的空行动。工作流完成与活动完成的对应条件见 [06](06-activities-and-workflows.md#lifecycle)。

## 3. 统一的模拟交互请求

所有需要经过模拟规则生效的行为均转为 `SimulationRequest`。普通函数直接返回请求；WorkflowBridge 将 MAF 的请求标识映射到同一合同。

| 字段 | 用途 |
|---|---|
| request_id | 稳定的模拟请求身份；另存当前 MAF 请求标识 |
| task_id、actor_id、activity_id? | 来源与发起权限 |
| kind、payload、schema_version | 请求类型及结构化参数 |
| correlation_id? | 关联邀请、消息、资源申请或其他请求 |
| atomic_group_id?、depends_on? | 必须联合处置的操作组及显式前置请求 |
| response_policy | 需要何种反馈、接收者及模板中的对应处理 |

请求类型包括 `environment_action`、`send_message`、`activity_control`、`wait_until` 和 `wait_message`。活动控制包含发起、加入、离开与取消。主体私有状态更新单独保存在 `actor_updates`，每项带 actor_id、field、operation、value 和可选 apply_if 条件；按字段规则合并并生成处置记录。

`SimulationResponse` 至少包含 request_id、outcome、result、visible_at、commit_id。响应进入下一次 ExecutionRequest；当前可见输入由 ObservationBuilder 重新构造。一个发送请求的“受理”反馈和消息“到达接收者”的事件分别记录。

发起者身份由运行适配器绑定，模型输出不能通过填写另一个 actor_id 获得其权限。请求只有出现在有效 SegmentResult 中并被提交后才可能产生效果。

<a id="interfaces"></a>

## 4. 主要接口

```text
ModelRegistry.validate(model_spec, execution_spec) -> ValidatedSpec
PopulationBuilder.initialize(validated_spec, seed) -> InitialState

Scheduler.select_due(snapshot) -> ReadyEvents
ActivityManager.plan(events, snapshot) -> ExecutionPlan
ObservationBuilder.build(plan, snapshot) -> list[ExecutionRequest]
async BehaviorExecutor.run(request) -> SegmentResult

EnvironmentRuntime.resolve(snapshot, events, requests) -> EffectPlan
ActivityManager.resolve(snapshot, results, effects) -> ActivityPlan
MessageRouter.plan(snapshot, results, effects, activities) -> DeliveryPlan
CommitManager.prepare(snapshot, results, effects, activities, deliveries) -> CommitBatch

RunStore.commit(owner_epoch, expected_version, batch) -> CommitReceipt
Scheduler.advance(receipt) -> ReadyEvents
```

EnvironmentRuntime 接收阶段事件，是为了让到期释放、自然变化等环境事件进入相同的后果处理。ActivityManager 的 `plan` 只安排执行，`resolve` 才形成生命周期候选变化，避免规划时提前修改成员或活动状态。

ExecutionPlan 保存目标、触发和任务集合；EffectPlan 保存行动处置、环境变化与定时后果；ActivityPlan 保存成员、生命周期和等待变化；DeliveryPlan 保存消息、反馈及投递时间。各计划在内存或候选载荷中计算，RunStore 是模拟状态的事务写入入口。

相互依赖的请求必须声明组合处理器或清晰的依赖顺序；计划间的原子组与依赖检查不通过时，CommitManager 拒绝整批提交。运行账目的任务登记与模型费用独立持久化，不能因此推进 state_version。

组件的随机数、只读查询和运行服务通过显式上下文注入。执行组件不能把 RunStore 写句柄传给模型工具；环境后果处理器在提交前不执行未登记的外部 I/O。

## 5. 身份、顺序与版本

| 身份 | 稳定范围 | 重试、恢复时的规则 |
|---|---|---|
| run_id | 一次运行 | 恢复保持；另开模型分支使用新 run_id |
| actor_id / activity_id | 一个运行内的长期对象 | 与 worker 无关，不随重建变化 |
| phase_id | 一个模拟坐标及阶段计划 | 重启复用已登记计划 |
| task_id | 目标对象在本阶段的一次激活 | 重试保持；活动多条到期输入合并为一次激活 |
| attempt_id | 一次执行尝试 | 重试更新，旧尝试失效 |
| request_id / message_id | 一项逻辑请求或消息 | 由 task_id、稳定来源节点/角色和该来源的发出序号派生；生效后固定 |
| call_id | 一次实际外部调用 | 再次调用生成新身份并关联来源 |
| owner_epoch | 协调进程所有权代次 | 新实例取得更高代次，拒绝旧实例提交 |

局部序号按逻辑来源维护，不按并发回调的到达顺序分配。MAF 的原生请求标识另存映射，重发继续使用已登记的模拟请求身份。

同一任务不同尝试可能产生不同候选内容；只有选定的有效尝试进入提交。具有相同身份却携带不同已提交内容的重复写入须报冲突，不能静默覆盖。

状态、请求、模板、提示渲染器和组件均带版本。恢复使用原版本及已提交检查点；升级需显式迁移并保留前后映射。流程图结构变更不与成员列表更新混为一类操作。

## 6. 模型装配时必须检查的条件

- 每个状态字段、资源和关系有确定的更新归属。
- 行为发出的操作已注册，所有必需反馈有处理路径。
- 群体和活动身份唯一；邀请、成员资格及退出规则可执行。
- 跨活动共享字段有合并或冲突策略，资源引用不形成第二份余额。
- 观察、记忆、工具和通信使用兼容的信息范围规则。
- 配置明确模拟时间单位、终止规则和即时阶段上限。
- 接续状态可序列化；模板和 executor 身份可以稳定重建。

静态检查只能发现组合错误。运行时的数据范围、资源争用与故障后状态还需 [12](12-implementation-and-acceptance.md) 的性质测试。
