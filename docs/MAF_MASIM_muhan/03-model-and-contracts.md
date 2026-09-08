# 03 · 模型装配与接口合同

[返回总览](README.md) · 前一篇：[总体架构](02-architecture.md) · 下一篇：[主体与记忆](04-agents-and-memory.md)

本文定义模块之间的数据边界。以下类型、字段与签名均为拟实现合同，尚不是可调用的 SDK；MAF 和 Ray 对象仅存在于相应适配层。

## 1. 模型由哪些组件组成

| 定义 | 主要内容 | 组合检查 |
|---|---|---|
| ActorDefinition | 角色、属性、行为、记忆和主体更新规则；可绑定 CompositeBehavior | 输入输出、内部身份、授权和字段归属 |
| PopulationDefinition | 主体模板、数量、分布、种子、关系生成器 | 身份唯一、分布有效、资源不重复分配 |
| BehaviorDefinition | 函数或 MAF 工厂、提示、工具、模型绑定和计算限额 | 输出合同、接续和工具能力兼容 |
| CompositeBehavior | SubAgent 定义、内部结构、调度与汇总策略 | 角色身份、信息传递、嵌套上限和对外授权 |
| MechanismDefinition | 记忆处理或环境辅助计算的输入、触发、依赖、输出和模型绑定 | 执行阶段明确、依赖无环、结果有消费规则 |
| EnvironmentDefinition | 模块、状态范围、操作、信息视图及定时规则 | 字段归属唯一、跨模块组合处理完整 |
| ActivityDefinition | 流程模板、参与条件、成员规则、等待和结束条件 | 流程版本、身份绑定、反馈处理 |
| Time / Visibility Policy | 激活、延迟、阶段、观察、通信与记忆规则 | 时间合法、接收者规则明确 |
| ModelBinding | provider 适配协议、model、可用 revision、解码设置 | 行为与机制引用有效，运行时可核对身份 |

ModelRegistry 将这些定义装配成 `ValidatedSpec`，保存规范化配置、组件版本与摘要。数据文件是可选输入，合成分布和声明假设可以直接初始化模型。

PopulationDefinition 按模板生成原子或复合主体。生成按 `run_seed + population_id + member_index` 派生稳定身份与随机流；复合主体内部再按角色定义键派生初始 subagent_id。生成参数和初始状态都保存。

主体及内部角色的后续创建、退出和停用通过生命周期提交生效，清理相应活动绑定、待响应关系和权限。已退役身份保留记录；再次创建同名角色使用新身份，防止迟到响应进入新角色。

## 2. 持久状态与可见输入

主体和活动描述模拟中的长期对象，行为实例记录一条流程的执行进度与等待位置。可见输入则按本次执行的身份、状态版本和模拟坐标构造。

| 类型 | 必要字段 | 含义 |
|---|---|---|
| ActorState | actor_id、definition_version、attributes、memory_refs、relation_refs、subagent_state_refs、independent_behavior_instance_id?、status | 对外模拟身份及其拥有的长期状态 |
| SubAgentState | actor_id、subagent_id、parent_subagent_id?、role_path、definition_version、attributes、memory_refs、status | 复合主体内部角色的持久状态，由父主体统一管理 |
| ActivityState | activity_id、template_version、members、member_version、status、behavior_instance_id | 活动的成员关系与领域生命周期 |
| BehaviorInstanceState | behavior_instance_id、owner_kind、owner_id、definition_version、status、continuation_ref?、binding_version_refs、pending_request_ids、control_event_refs、deferred_event_refs、context_scope | 一条独立行为或活动流程的进度与恢复入口 |
| SnapshotView | run_id、state_version、coord | 指定版本的只读视图，按需装载 |
| ActorView | view_id、actor_id、subagent_id?、activity_id?、behavior_instance_id、state_version、coord、visible_fields、inbox、memory、capabilities | 本次行为中某个身份可见的信息 |
| MechanismView | view_id、component_id、subject_ref、state_version、coord、input_refs、access_scope | 一项记忆或环境计算得到的授权输入 |
| ResumeInput | behavior_instance_id、coord、read_version、view_refs、responses、control_events、digest | 一次接续的完整输入及其摘要 |

BehaviorInstanceState 通过 owner_kind 归属于主体或活动。**continuation_ref 和 pending_request_ids 的唯一生效位置是行为实例**，ActorState 与 ActivityState 仅关联实例身份。嵌套工作流和局部会话从这一入口恢复；长期 SubAgentState 从所属 ActorState 恢复，checkpoint 不覆盖长期状态。

行为实例状态为 ready、waiting、completed、cancelled 或 failed；必需反馈与清理完成后才能进入终止状态，执行尝试的 running 状态单独记录。一个实例在一个模拟阶段最多有一个行为任务及一个选中尝试。独立主体默认只保留一条未结束的独立行为实例；持续活动各有自己的实例。

同一复合主体参与 X、Y 时，内部角色的长期身份保持一致，局部会话按 `run / behavior_instance / actor / role_path` 隔离。可见视图由适配器逐身份传入，不能把全部参与者视图映射整体交给一个模型。

## 3. 执行任务与结果

| 类型 | 必要字段 | 含义 |
|---|---|---|
| PhasePlan | phase_id、coord、read_version、event_refs、stage_rules、sealed_task_sets、selected_candidates | 固定阶段输入，并保存各工作阶段的任务与依赖 |
| ExecutionRequest | run_id、task_id、attempt_id、owner_epoch、coord、read_version、task_kind、work_stage、target、input_refs、dependency_refs、resume_input?、limits | 共享执行池的一次执行尝试 |
| SegmentResult | task_id、attempt_id、read_version、requests、actor_updates、continuation_ref?、pending_request_ids、disposition、record_refs | 完整行为片段的候选结果 |
| MechanismResult | task_id、attempt_id、read_version、output_ref、record_refs | 记忆或环境辅助计算的候选结果，不直接提出世界修改 |
| DispositionPlan | request/group/update 身份、outcome、reason、allocations、conditional_changes、feedback、causal_refs | 跨模块共同使用的最终处置 |
| CommitBatch | commit_id、phase_id、expected_version、selected_attempts、state_changes、events、record_refs | 本阶段准备生效的联合变化 |
| CommitReceipt | commit_id、state_version、coord、event_refs | 已生效版本及后续事件 |

task_kind 为 behavior 或 mechanism。前者的 target 指向 behavior_instance_id；后者指向 component_id 与 subject_ref，例如 A 的记忆或某组环境申请。两类任务共用执行尝试、预算、结果保存和恢复协议，分别返回 SegmentResult 与 MechanismResult。

work_stage 分为 prepare、behavior、adjudicate，表示一个模拟阶段内的输入准备、行为计算和后果辅助计算。它们不推进模拟时间；依赖规则见 [07](07-time-and-communication.md)。纯检索可在协调侧读取固定视图，涉及模型的摘要、反思和判断须登记执行任务。

SegmentResult.disposition 表示本片段完成后等待还是结束。执行异常保存为尝试失败；出现一条流式输出不代表结果完整。机制输出由声明的 MemoryPolicy、ActorStatePolicy 或环境规则消费，不能绕过处置和提交直接生效。

## 4. 统一的模拟交互请求

所有经过模拟规则生效的交互均转为 `SimulationRequest`。普通函数直接返回请求；WorkflowBridge 将 MAF 请求映射到同一合同。

| 字段 | 用途 |
|---|---|
| request_id | 稳定模拟请求身份；另存当前 MAF 请求标识 |
| task_id、behavior_instance_id、actor_id、subagent_id?、role_path?、activity_id? | 来源、接续位置和权限核对 |
| kind、payload、schema_version | 请求类型与结构化参数 |
| correlation_id? | 关联邀请、消息、资源申请或其他请求 |
| atomic_group_id?、depends_on? | 必须联合处置的操作组及显式前置请求 |
| response_policy | 反馈种类、接收范围、等待及消费规则 |

类型包括 `environment_action`、`send_message`、`activity_control`、`actor_control`、`wait_until` 和 `wait_message`。actor_control 处理主体及内部角色的授权创建、停用与绑定变更，和活动控制一样进入联合处置。内部角色以父主体 actor_id 对外提出请求，subagent_id 用于来源与内部授权核对；权限不能超过父主体授予的范围。

主体候选更新保存在 actor_updates，每项带 update_id、actor_id、subagent_id?、field、operation、value、source_ref 和可选 apply_if。长期角色更新也经父主体规则合并，不能直接修改另一个主体或角色的状态。

`SimulationResponse` 包含 response_id、request_id、recipient_scope、outcome、result_ref、visible_at、commit_id。一个请求可以按协议关联不同种类的反馈，每项逻辑反馈有独立 response_id。发送受理与到达接收者分别记录。

身份由运行适配器绑定，模型输出不能自行扩权。请求仅在有效 SegmentResult 被采纳并提交后产生模拟效果；恢复时重新构造当前视图并封装响应，见 [06](06-activities-and-workflows.md#bridge)。

<a id="interfaces"></a>

## 5. 主要接口

```text
ModelRegistry.validate(model_spec, execution_spec) -> ValidatedSpec
PopulationBuilder.initialize(validated_spec, seed) -> InitialState

Scheduler.select_due(snapshot) -> ReadyEvents
BehaviorManager.plan(events, snapshot, activity_bindings) -> PhasePlan
ObservationBuilder.build(scope, snapshot, admitted_inputs) -> ActorView
MechanismPlanner.plan_stage(phase, selected_upstream) -> StageTaskSet
RunStore.seal_stage(owner_epoch, stage_tasks, input_refs) -> SealedTaskSet
async BehaviorExecutor.run(request) -> SegmentResult
async MechanismExecutor.run(request) -> MechanismResult

ResolutionCoordinator.resolve(snapshot, events, segments, mechanism_results)
    -> DispositionPlan
EnvironmentRuntime.plan(snapshot, events, dispositions) -> EffectPlan
ActivityManager.plan_changes(snapshot, dispositions) -> ActivityPlan
ActorStatePolicy.plan(snapshot, segments, mechanism_results, dispositions) -> ActorPlan
BehaviorManager.plan_changes(snapshot, segments, dispositions) -> BehaviorPlan
MessageRouter.plan(snapshot, dispositions, activities) -> DeliveryPlan
CommitManager.prepare(phase, dispositions, effects, activities, actors, behaviors, deliveries)
    -> CommitBatch

RunStore.commit(owner_epoch, expected_version, batch) -> CommitReceipt
Scheduler.advance(receipt) -> ReadyEvents
```

ActivityManager 管理成员与活动规则，BehaviorManager 统一管理主体和活动的行为实例、触发合并及等待索引。新实例先作为阶段计划中的候选登记，随创建操作提交生效；规划执行不提前修改模拟状态。

ResolutionCoordinator 调用注册的领域验证器与组合处理器，形成唯一处置。各模块依据同一处置生成更新计划，操作的成败以该处置为准。普通非法请求产生拒绝反馈；缺少必要处理器或计划互相矛盾属于配置或运行错误，暂停提交。联合分配方法见 [05](05-environment-and-actions.md)。

运行账目的任务登记、阶段封存和调用费用独立持久化，不推进 state_version。协调与后果计算接口只使用已登记任务提供的模型结果。

## 6. 身份、顺序与版本

| 身份 | 稳定范围 | 重试、恢复时的规则 |
|---|---|---|
| run_id | 一次运行 | 恢复保持；新的模型定义使用新运行 |
| actor_id / subagent_id / activity_id | 运行内的长期对象 | 与 worker、会话对象及显示名称无关 |
| behavior_instance_id | 一条持续行为流程 | 等待和重建不变，结束后新流程使用新身份 |
| phase_id / task_id | 一个模拟阶段 / 一项逻辑任务 | 重启复用；同实例的到期输入合并 |
| attempt_id | 一次执行尝试 | 重试更新；选中候选和失效状态持久保存 |
| request_id / message_id | 一项逻辑请求或消息 | 从 task、稳定节点/角色及来源序号派生 |
| response_id | 一项逻辑反馈 | 重投保持，同身份不同内容报冲突 |
| call_id | 一次实际外部调用 | 再次调用生成新身份并关联来源 |
| owner_epoch | 协调所有权代次 | 新实例取得更高代次，拒绝旧实例写入 |

局部序号按逻辑来源维护，不按并发回调的到达顺序分配。MAF 原生请求标识另存映射，重发使用原模拟请求身份。上游候选一旦用于派生后续任务，须先封存选定引用，恢复复用同一内容。

ModelBinding 进入模型定义摘要；EndpointBinding 将其映射到连接地址、凭据引用和配额，属于执行配置。模型 revision、解码参数、提示或输出 schema 的调整属于模型变化，按模型定义管理。具体核对见 [08](08-execution-and-scaling.md#model-binding)。

状态、请求、模板、提示渲染器和组件均带版本。恢复使用原定义和已提交接续位置；升级需显式迁移并保留映射。成员或内部角色的数据更新通过已提交 control events 应用于接续数据，与流程图结构迁移分别处理。

## 7. 模型装配检查

- 每个状态字段、资源、内部角色和会话有唯一更新与恢复归属。
- 内部角色结构无环、嵌套与局部计算有上限，对外授权和汇总策略完整。
- 行为操作已注册，必需反馈有处理路径，独立等待也有持久接续位置。
- 群体、主体与活动身份唯一，加入、退出和迟到响应规则可执行。
- 组合操作有处理器及有界依赖规则，共享字段有合并或冲突策略。
- 观察、记忆、工具和通信遵守兼容的信息范围。
- 机制计算的阶段、输入依赖、模型绑定和结果消费规则明确。
- 模拟时间单位、终止条件、即时阶段上限与恢复版本明确。

静态检查只能发现组合错误。数据范围、资源争用与故障后的状态还需 [12](12-implementation-and-acceptance.md) 的性质测试。
