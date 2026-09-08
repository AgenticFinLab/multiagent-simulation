# 10 · 使用方式、观测与扩展入口

[返回总览](README.md) · 前一篇：[状态与恢复](09-state-and-recovery.md) · 下一篇：[迁移与工程](11-migration-and-engineering.md)

## 1. 装配模型与执行配置

模型组件采用 Python 接口，配置文件引用注册组件及参数。以下是职责分工示意，字段尚未形成正式 schema。

```yaml
model:
  population: community_population
  actors: atomic_and_composite_actors
  behaviors: community_behaviors
  mechanisms: memory_and_environment_mechanisms
  environment: shared_resources
  activities: negotiation_and_cooperation
  time_policy: discrete_events
  visibility_policy: member_and_role_scoped
  seed: 42
  model_bindings:
    deliberation:
      provider_adapter: selected_maf_adapter
      model_id: configured_model
      model_revision: null
      decoding:
        temperature: 0.2
        max_output_tokens: 1024

execution:
  pool: ray
  function_workers: 2
  maf_workers: 2
  endpoint_bindings:
    deliberation:
      connection_profile: research_endpoint
      credential_ref: research_model_credential
      quota_group: shared_research_quota
  max_inflight_tasks: 16
  budget_profile: controlled_probe
  store_profile: local_postgres_and_blobs
  on_runtime_error: pause
```

model 部分定义主体、环境和行为机制，并保存模型身份与解码参数；execution 部分配置 worker、端点连接和预算。行为、内部角色与辅助计算均可引用相应模型绑定。

EndpointBinding 通过连接配置提供地址与 deployment，凭据仅保存引用。示例中的空 revision 表示没有提供可固定的模型版本标识，其核验状态需在运行记录中说明。

初始化按定义展开群体和环境，保存初态与事件。提示、工具、记忆、角色结构、时间、信息和结果 schema 均有版本。实际模型核对方法见 [08](08-execution-and-scaling.md#model-binding)，worker 数不构成性能承诺。

## 2. 运行操作

| 拟提供操作 | 用户看到的结果 |
|---|---|
| validate | 组件、角色、权限、依赖、模型绑定与恢复能力检查 |
| start | run_id、定义摘要、模型核对状态和初始位置 |
| status | 当前坐标、工作阶段、提交版本、执行/等待任务及预算 |
| inspect actor / subagent | 父主体身份、角色状态、长期记忆和授权来源 |
| inspect activity / behavior-instance | 成员、局部会话范围、待请求、接续位置和推迟触发 |
| pause / resume / stop | 明确操作状态、配置核对与可恢复位置 |
| check | 信息、资源、身份、组合处置、提交和接续性质报告 |
| export / replay | 指定范围的记录及回放检查结果 |

先提供 Python 与 CLI，界面复用相同接口。首版以单研究团队受控运行配置为边界，多租户及复杂操作界面另行扩展。

运行状态区分 running、paused、quiescent、completed、failed、stopped，并单独显示 pausing。查询接口只读，不因 inspect 一个主体而触发反思或重新调用模型。

## 3. 三类记录

| 记录 | 内容 | 保留规则 |
|---|---|---|
| 恢复与生效 | 阶段任务、输入依赖、选中候选、状态、处置、投递与接续位置 | 完整保存至恢复保留期结束 |
| 行为与来源 | 角色视图、调用响应、汇总、行动、反馈和消息关联 | 需复核行为的运行保留完整引用 |
| 运行诊断 | 日志、耗时、队列、worker 和调试指标 | 可配置采样与保留期 |

RunRecorder 通过 run_id、actor_id、subagent_id、role_path、activity_id、behavior_instance_id、task_id、attempt_id、request_id、response_id、call_id 和 commit_id 关联记录。机制任务另记 component_id、subject_ref、work_stage 与上游来源。

每次外部调用记录声明绑定和实际模型标识。从一次资源请求可以追溯到主体看到的信息、决策结果、环境处置和后续反馈；使用复合行为时，还能展开内部建议与汇总过程。环境辅助判断也保留独立来源。

模拟坐标与墙钟时间分别保存。记录实际请求、可见响应、结构化结果和工具输出，无须保存模型未提供的内部推理。执行来源关系不直接证明经验因果效果。

## 4. 指标与诊断

| 维度 | 核心指标 | 用途 |
|---|---|---|
| 持续规模 | 对外主体、内部角色、行为实例、状态字节与等待索引 | 分别描述持久对象容量 |
| 工作吞吐 | prepare / behavior / adjudicate 任务、处置与投递速率 | 区分真正完成的工作 |
| 延迟分解 | 排队、装载、各工作阶段、屏障、联合处置、提交 | 定位瓶颈 |
| 模型使用 | 绑定、角色或机制、调用、token、预留、实际/估计费用、unknown | 解释成本且避免重复汇总 |
| 可靠性 | 失效尝试、重复响应、迟到反馈、恢复耗时 | 检查故障与身份协议 |
| 模型结构 | 活跃率、角色深度、通信密度、成员数与重叠度 | 描述负载复杂度 |

报告同时列明硬件、worker、响应分布、状态体积与模型设置。token 吞吐不能替代共享世界的处置和提交能力。

## 5. 系统检查与轨迹输出

检查器覆盖信息范围、状态归属、资源约束、活动与角色生命周期、时间顺序、重复效果、接续完整性和账目一致。报告附可定位身份和记录。

通用轨迹首先服务调试、恢复与组件比较，后续 EPG 对接采用：

```text
通用过程记录 → 独立 EPG 适配器 → 事件图展示与领域分析
```

对外事件以 actor_id 组织，内部角色与行为实例作为来源展开。保存请求—反馈、模拟时间与提交关联，为适配提供基础；领域词表、事件粒度和科学评价后续单独设计。

<a id="extensions"></a>

## 6. 外部协议入口

| 需求 | 接入位置 | 合同要求 |
|---|---|---|
| 知识与工具服务 | MAF 工具 / MCP 适配 | 来源范围、结果记录、只读或副作用分类 |
| 远端 Agent | BehaviorExecutor 或活动参与者适配 | 身份、可见输入、请求响应及恢复 |
| 人在环 | 运行控制与活动外部输入 | 输入内容、操作者与模拟坐标有记录 |
| 观察面板 | 只读状态与记录 API | 不直接改写模拟状态 |

协议适配复用 MAF 生态，具体包在需要时核验。首版不要求全部协议同时产品化。内部主体高频通信采用 MessageRouter；跨系统连接也遵守相同的身份、时间与反馈合同。
