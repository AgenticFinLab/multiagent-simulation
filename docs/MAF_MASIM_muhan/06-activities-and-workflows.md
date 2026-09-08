# 06 · 持续活动与 MAF 工作流

[返回总览](README.md) · 前一篇：[环境与行动](05-environment-and-actions.md) · 下一篇：[时间与通信](07-time-and-communication.md)

## 1. 为什么将活动作为持续对象

协商、共同计划和任务合作具有成员、局部记录与结束条件，经常需要等待模拟世界中的答复。ActivityState 保存这种持续关系，MAF Workflow 保存局部流程的执行进度。

一次活动可以多次获得 worker，执行后返回等待状态。同一主体可以同时属于多个未结束活动；参与关系由模拟模型管理，物理并发由执行池管理。

MAF 负责活动内部的分支、函数和 Agent 调用。新系统补充活动登记、成员权限、模拟时间、信息路由与全局提交，无须复制一套 MAF 内部图执行器。

<a id="lifecycle"></a>

## 2. 活动生命周期

| 持久状态 | 含义 | 转移条件 |
|---|---|---|
| ready | 可以启动或接续 | 初始登记或等待条件已满足 |
| waiting | 已返回模拟边界 | 有必需请求尚未得到允许可见的响应 |
| completing | 已提出结束，仍有必要反馈或清理 | 等待最后处置、释放资源或通知成员 |
| completed | 正常结束 | 结束条件满足，必需请求已处置 |
| cancelled | 按模型规则取消 | 完成取消规则所要求的清理 |
| failed | 活动被明确终止为失败 | 采用了已声明的活动失败策略 |

“正在某个 worker 执行”保存在运行尝试表中，不提前改写 ActivityState。每项活动在一个阶段最多有一个有效任务、一个有效尝试；多条到期响应合并到这个任务。

waiting 活动在当前坐标收到所需响应时，ActivityManager 可以安排接续；其持久状态仍保留到本阶段提交后再更新。这样无需为开始计算先写入一次模拟状态。

运行错误默认使 run 暂停并保留最近已提交的活动状态。只有模型明确规定某类失败是活动终止事件时，才提交 `failed` 及相应后果。

创建、加入、退出、取消均为 activity_control 请求。成员变化在提交后生效，下一片段使用新成员版本。成员退出需取消其待响应关系、处理角色和资源，并为剩余成员提供允许可见的反馈。

## 3. MAF 复用范围

| MAF 构件 | 系统中的用途 | 需要新增的适配 |
|---|---|---|
| Agent / model client | 决策、结构化输出、工具循环 | 主体绑定、输入投影和统一结果合同 |
| Workflow / Executor | 局部分支、并行计算、内部协作 | 活动模板和成员调度 |
| Session / Context Provider | 私有会话和上下文装配 | 身份隔离、记忆归属及恢复校验 |
| request / response | 暂停依赖反馈的路径，随后继续 | SimulationRequest / Response 映射 |
| checkpoint | 保存局部执行状态 | 候选与已提交引用的区分 |
| middleware / tracing | 调用拦截和观测 | 共享配额、尝试关联、用量记账 |

MAF 的请求机制允许自定义 Executor 请求外部信息，并在恢复时提交响应。本设计通过 SimulationRequest 与 WorkflowBridge 将该机制适配为模拟反馈。[MAF 请求与响应](https://learn.microsoft.com/en-us/agent-framework/workflows/human-in-the-loop)

<a id="bridge"></a>

## 4. WorkflowBridge 的执行合同

一个**执行片段**从本次启动或恢复开始，到局部可运行路径完成、等待模拟反馈或流程结束为止。只有片段完整返回后，结果才进入全局候选集合。

```text
已提交 ActivityState + ActorViews + 可见响应
  → 构建或恢复相同版本的 MAF Workflow
  → 运行局部函数、Agent 与内部协作
  → Bridge 发出模拟请求，依赖反馈的路径停止
  → 当前可运行路径排空，校验并保存 checkpoint
  → 返回 SegmentResult
  → 系统提交后果、等待关系与 continuation_ref
  → 后续模拟坐标到达，提供响应并继续
```

Python 参考入口是 `ctx.request_info()`、`@response_handler` 和 `workflow.run(responses=..., checkpoint_id=...)`。它们的组合需要在固定版本下验证；本文不把示意流程当作已可直接运行的 SDK 样例。

Bridge 须满足以下条件：

1. 给每个模拟请求分配稳定 request_id，保存其与 MAF 请求标识的映射。
2. 在本片段所有可运行路径排空后形成结果；流中出现第一条请求不触发提前提交。
3. checkpoint、请求集合和参与者状态相互对应；失败或不完整片段不提交部分结果。
4. 接续只消费已提交且到达可见坐标的响应，重复响应不会再次产生效果。
5. 更新当前 ActorView，同时保留合法的历史会话；恢复不等于继续使用旧的环境观察。
6. 达到步骤、工具或模型调用上限时形成明确运行错误，避免无界局部执行阻止返回。

MAF 文档说明 pending requests 随 checkpoint 保存，恢复时可重新发出请求。因此适配器必须按 request_id 识别已经登记的等待，不能把重发视作新申请。[检查点中的请求](https://learn.microsoft.com/en-us/agent-framework/workflows/human-in-the-loop#checkpoints-and-requests)

## 5. 三种边界调用

| 请求 | 本次片段返回什么 | 下次如何继续 |
|---|---|---|
| 申请资源或改变环境 | 候选行动与待响应位置 | 接受、拒绝或无效果处置进入对应处理器 |
| 向另一主体发送消息 | 消息请求、发送反馈或答复等待 | 发送受理和对方答复分别关联；答复可在更晚坐标到达 |
| 等待时间、消息或条件 | 订阅条件、期限与 checkpoint | Scheduler / MessageRouter 触发响应后恢复 |

消息等待需要关联键和消费策略，支持等待任一或全部指定响应。模板声明期限及超时分支；无限等待允许存在，但系统要能报告其原因。等待期间资源占用由环境预约规则决定。

如果所有活动都在等待且没有可达事件，运行进入 `quiescent`，输出等待关系。只有达到模型完成条件才标记完成；互相等待不会因事件队列为空而被当作成功。

## 6. 多主体交互与信息范围

独立模拟主体之间的消息和反馈经 Bridge 返回模拟边界，随后按消息规则投递。单个主体内部的辅助角色可以在片段内协作。此区分决定信息何时传播，也决定一次工作流包含多少模拟阶段。

标准 Group Chat 默认会形成共享对话上下文；直接套用到含私有信息的多主体活动会扩大信息范围。活动模板应使用参与者专属视图和显式消息节点，只有模型声明的共享内容才能进入公共上下文。[MAF Group Chat](https://learn.microsoft.com/en-us/agent-framework/workflows/orchestrations/group-chat)

MAF Worker 内的可信适配代码负责路由，不能把包含所有参与者私有输入的字典整体渲染给某个模型。此处保证的是组件遵守合同的信息隔离；执行不可信第三方代码所需的进程安全隔离属于额外部署能力。

## 7. 检查点与动态成员

采用稳定的流程模板和 executor 身份。成员列表、角色分配和成员私有会话作为活动数据保存；参加或退出通过数据更新绑定。参与者调度节点需能在固定图结构下管理这个集合，并实现对应状态序列化。

MAF 要求恢复时保持工作流结构和 executor 身份。增减固定图节点属于模板迁移，应在显式迁移位置生成新版本，不能把旧 checkpoint 交给另一张图。[MAF checkpoint 恢复](https://learn.microsoft.com/en-us/agent-framework/workflows/checkpoints)

优先使用可以完整本地序列化的会话。参考源码中的 AgentExecutor 会保存会话与待响应状态，但也存在恢复异常后重新创建会话的路径；服务端会话指针可能不包含完整历史。适配器需要校验恢复后的成员、会话内容、请求与模板，失败时停止接续。[参考 AgentExecutor 源码](https://raw.githubusercontent.com/microsoft/agent-framework/python-1.17.0/python/packages/core/agent_framework/_workflows/_agent_executor.py)

动态成员、并发分支和跨 worker 的完整恢复是首轮关键探针，尚未获得新系统集成证据。若原生构件无法保持这些条件，应在 MAF 适配层补齐状态协议并重新验收。

## 8. 重叠参与的处理

X、Y 分别保存 A 的成员会话，都从本阶段已提交状态构造 A 的视图。双方可以并行提出资源申请，环境按同一批规则处置。长期记忆追加可按稳定顺序合并；其他共享字段按声明规则处理。

一个活动被取消不会清空另一活动的会话或终止主体身份。若模型认为 A 的注意力或工作时间有限，应将其定义为环境资源或参与约束；系统并发上限仅管理计算资源，不能暗中替代该建模决定。
