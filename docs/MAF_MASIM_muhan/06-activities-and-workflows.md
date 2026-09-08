# 06 · 持续活动与 MAF 工作流

[返回总览](README.md) · 前一篇：[环境与行动](05-environment-and-actions.md) · 下一篇：[时间与通信](07-time-and-communication.md)

## 1. 活动与行为实例的分工

协商、共同计划和任务合作具有成员、局部记录与结束条件，经常需要等待模拟世界中的答复。ActivityState 保存这些活动关系；BehaviorInstanceState 保存执行进度和等待位置，MAF Workflow 承载其中的局部流程。

| 场合 | 领域对象 | 行为实例归属 |
|---|---|---|
| A 独立申请资源并等待反馈 | ActorState A | actor：A |
| A 的多个内部角色共同决策 | ActorState A + SubAgentState | A 的独立实例，或 A 所参与的活动实例 |
| A、B、C 持续协商 X | ActivityState X | activity：X |

BehaviorManager 为独立行为和活动流程统一安排启动、等待与接续；ActivityManager 管理活动的成员关系及生命周期。

一条流程可以经过多次调度：每次由 worker 执行可推进的部分，保存进度后释放计算资源。同一主体可以参加多个未结束活动，每个活动持有独立实例。MAF 管理内部节点和分支，新系统管理模拟时间、权限、等待与提交。

<a id="lifecycle"></a>

## 2. 生命周期与激活

| 对象 | 状态 | 转移规则 |
|---|---|---|
| 行为实例 | ready / waiting | 新建或到期输入使流程可推进；返回模拟边界后等待 |
| 行为实例 | completed / cancelled / failed | 正常结束、按规则取消或模型声明的终止失败 |
| 活动 | ready / active | 创建生效后等待启动；启动后活动持续存在 |
| 活动 | completing | 已提出结束，仍需反馈、资源释放或成员通知 |
| 活动 | completed / cancelled / failed | 对应结束条件及必需清理均已满足 |

活动的等待情况由关联行为实例记录。活动保持 active 时，其实例可以处于 waiting；只有必需反馈和清理完成后，活动才进入 completed。模板据此定义结束条件与清理路径。

worker 的执行进度记录在尝试表中。一个行为实例在一个模拟阶段最多有一个行为任务及一个选中尝试，多条到期响应合并到同一 ResumeInput。规划时不提前修改其已提交状态。

独立主体已有未结束实例时，普通周期触发按定义合并或存入 deferred_event_refs；仅能通过模板声明的输入请求唤醒等待中的路径。实例结束后再启动下一次独立流程，保留待响应工作流的原始输入与接续状态。

创建、加入、退出、取消采用 activity_control 请求，成员变化在提交后生效。内部角色变化通过 actor_control 按复合主体生命周期合同处理。取消与退出产生待请求处置、资源清理及允许可见的通知；它们与其他后果使用同一联合处置。

运行错误默认暂停 run，保留已提交状态。只有模型声明某类失败是模拟中的终止事件时，才提交 failed 及其后果。

## 3. MAF 复用范围

| MAF 构件 | 用途 | 新系统适配 |
|---|---|---|
| Agent / model client | 决策、结构化输出、工具循环 | 主体与角色绑定、模型身份和统一结果合同 |
| Workflow / Executor | 局部分支、并行、委派与复合行为 | 固定流程模板、成员及角色调度 |
| 嵌套 Workflow | 复用角色协作或局部子流程 | 独立实例、接续位置与有界嵌套 |
| Session / Context Provider | 局部会话和上下文装配 | 当前视图、私有范围、长期状态引用 |
| request / response | 停止依赖反馈的路径并接续 | 模拟请求、响应信封与去重 |
| checkpoint | 局部执行状态 | 候选与已提交引用、完整性检查 |
| middleware / tracing | 调用拦截和观测 | ModelAccess、尝试关联和用量记录 |

嵌套流程可以作为自定义 Executor 的子工作流；需要 Agent 接口的场合再使用 Workflow-as-Agent 适配，并核对其消息输入合同。复合主体不要求所有子角色都包装成同一种 Agent。[MAF Workflow-as-Agent](https://learn.microsoft.com/en-us/agent-framework/workflows/as-agents)

每个行为实例及执行尝试使用独立的 Workflow、Executor 和 Session 对象。可共享缓存包括不可变定义和流程工厂。

<a id="bridge"></a>

## 4. WorkflowBridge 如何接收反馈并继续

一个**执行片段**包含启动或恢复后当前能够推进的全部路径。各路径执行完毕、等待模拟反馈或结束流程后，才返回完整的候选结果。

```text
已提交 BehaviorInstanceState + 当前 ResumeInput
  → 恢复同版本流程、局部会话和请求映射
  → 绑定本次调用的当前身份视图
  → 向等待节点提供带当前视图引用的响应
  → 运行局部函数、Agent 与内部协作
  → 发出模拟请求，依赖反馈的路径停止
  → 当前可运行路径全部完成或等待，保存完整 checkpoint
  → 返回 SegmentResult
  → 联合提交后果、响应消费、等待关系和新接续位置
```

桥接层用 **SimulationGateway Executor** 连接模拟反馈与工作流。节点通过 `ctx.request_info()` 请求反馈，并声明响应类型为 `SimulationResumeEnvelope`；`@response_handler` 接收后继续对应路径。信封包含一项 SimulationResponse、接收身份、当前 ActorView 引用和输入摘要，内容均限于该身份的授权范围。

| 调用情形 | 输入路径 | 合同要求 |
|---|---|---|
| 初次启动 | 流程声明的初始 message | 绑定当前视图并建立来源身份 |
| 等待后接续 | `workflow.run(responses=..., checkpoint_id=...)` | responses 映射使用原 MAF 请求标识，不同时传初始 message |
| 部分响应到达 | 只向对应等待节点提供有效信封 | 保留其余待请求，保存新的完整接续状态 |
| 取消、退出等控制 | 已声明的控制/反馈路径 | 校验当前身份，执行清理，不让停用角色继续获得行动权限 |

固定版本的 MAF 接口中，初始 message 与 responses 不能混用。仅恢复 checkpoint 也不会自动替换其中的旧观察；桥接层必须显式提供新的输入。[参考 Workflow 源码](https://github.com/microsoft/agent-framework/blob/4507512f95effaae4518d658e86e9afc0ccb4514/python/packages/core/agent_framework/_workflows/_workflow.py)

恢复后，适配器通过当前调用上下文（**CurrentInvocationContext**）按主体或子角色身份提供 ActorView。这份上下文在本次调用期间保持不变，供 Agent、上下文装配和模拟查询共同使用；checkpoint 中的旧观察保留为带坐标的历史内容。当前调用上下文独立于 checkpoint，不承担长期状态保存。

没有有效接续输入时不调用等待中的流程。控制输入只能进入模板已声明的通道；角色退出后的清理由可信模板代码处理，相关模型调用与工具权限先经过当前身份校验。

## 5. 请求、重复响应与片段完整性

| 情况 | Bridge 与持久记录的处理 |
|---|---|
| checkpoint 恢复后重新发出待请求 | 按原映射识别，不生成第二项模拟申请 |
| 同一 response_id 重投 | 内容一致时在进入 SDK 前去重；已消费则返回原处置 |
| 相同身份却内容不同 | 报告冲突，保留记录，不覆盖 |
| 回复已取消、已结束或已退出的路径 | 记录迟到/失效处置，不重新唤醒 |
| 仅部分请求获得响应 | 接续可运行分支，其余等待仍在新 checkpoint 中 |
| 某分支输出后其他分支失败 | 尝试失败，不提交流出的部分结果 |

MAF 会持久化 pending requests，并可能在恢复时重新发出；应用需要维护请求身份。[MAF 请求与检查点](https://learn.microsoft.com/en-us/agent-framework/workflows/human-in-the-loop#checkpoints-and-requests)

去重由 Bridge 和 RunStore 完成，不依赖 SDK 把重复 responses 自动视为空操作。响应的“已消费”随阶段结果提交；提交前失败的尝试可以从原接续位置重试，旧尝试对象不继续使用。

checkpoint、角色会话、待请求和来源映射必须一致。达到计算上限、恢复不完整或分支异常时停止该尝试，避免以空结果或缺失会话继续模拟。

## 6. 三种边界调用

| 请求 | 本次返回 | 后续接续 |
|---|---|---|
| 申请资源或改变环境 | 候选行动与待响应位置 | 接受、拒绝或无效果反馈进入对应路径 |
| 发送消息并等待答复 | 发送请求、受理反馈及答复等待 | 发送受理与对方答复分别关联 |
| 等待时间、消息或条件 | 订阅条件、期限与 checkpoint | 时间或消息事件在允许坐标触发反馈 |

模板声明关联键、any / all 消费规则、期限与超时分支。单个等待请求先由等待规则汇集匹配消息，条件满足、期限到达或取消时再形成逻辑反馈；多个独立请求可以分批响应。等待释放 worker，模拟资源则遵守预约和释放规则。

所有实例都在等待且没有可达事件时，run 进入 quiescent 并报告等待关系。模型完成条件满足后才进入 completed。

## 7. 多主体与内部角色的信息范围

独立模拟主体之间的消息经 Bridge 返回模拟边界，按时间与路由规则投递。复合主体内部的角色可以按声明的信息和耗时规则在局部片段内协作；内部通信不自动成为对外消息。

标准 Group Chat 会形成共享对话上下文。含私有信息的活动应使用参与者专属视图与显式消息节点，只将允许共享的内容放入公共上下文。[MAF Group Chat](https://learn.microsoft.com/en-us/agent-framework/workflows/orchestrations/group-chat)

可信适配代码可以路由视图引用，每次模型调用只获得绑定身份的内容。此处是遵守合同的组件隔离；不可信第三方代码的进程安全隔离属于额外部署能力。

## 8. 嵌套、成员变化与恢复

采用稳定流程模板和 executor 身份；成员、内部角色绑定与私有会话作为数据管理。固定调度节点按已提交成员和角色版本运行，并保留退出身份的请求处置记录。动态绑定能力需要适配器实现与验证，不能从嵌套工作流支持直接推导。

成员或角色变化可能先于原工作流下一次接续生效。此时同时保存原 checkpoint 的 binding_version_refs 与待应用 control_event_refs：先按原绑定恢复，再由可信调度节点应用已提交变更，随后执行当前授权的路径。控制变更的消费记录与新 checkpoint 共同提交。

取消提交生效时，相应世界权限和等待条件按模型规则失效；需要清理的 SDK 待请求仍保留原映射，以取消反馈推进清理。普通迟到答复不再接纳。必需清理结束后才提交实例及活动的终止状态，避免留下无人接续的旧请求。

嵌套流程的 checkpoint 与请求映射归入顶层行为实例的接续位置；角色长期状态仍由父主体保存。改变图节点或执行器结构属于模板迁移，不能把旧 checkpoint 交给另一张图。[MAF checkpoint 恢复](https://learn.microsoft.com/en-us/agent-framework/workflows/checkpoints)

AgentExecutor 可保存会话与待请求，但参考实现也存在恢复异常后创建新会话的路径。适配器须检查会话内容、角色、模板及请求完整性，失败时停止接续。[参考 AgentExecutor 源码](https://github.com/microsoft/agent-framework/blob/4507512f95effaae4518d658e86e9afc0ccb4514/python/packages/core/agent_framework/_workflows/_agent_executor.py)

验收分别覆盖跨进程嵌套、真实 Agent 会话、角色变化与全局事务接续，再通过集成用例检查它们能否共同恢复。

## 9. 重叠参与

X、Y 分别保存 A 及其内部角色的局部会话，读取同一阶段已提交的长期状态。角色在 X 中的私有讨论不会进入 Y 的提示；允许保留的长期更新在提交后按可见性规则共享。

两项活动提出的行动仍归于 A，资源请求进入同一联合处置。长期记忆追加按稳定顺序合并；不可合并字段采用声明的优先级或拒绝规则。

取消 X 只终止 X 的局部路径及相应资源关系，A、其长期角色状态和 Y 继续存在。若 A 的注意力或工作时间有限，将其定义为环境资源或参与约束；执行并发限制只管理计算。
