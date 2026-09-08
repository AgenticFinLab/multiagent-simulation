# 10 · 使用方式、观测与扩展入口

[返回总览](README.md) · 前一篇：[状态与恢复](09-state-and-recovery.md) · 下一篇：[迁移与工程](11-migration-and-engineering.md)

## 1. 使用者怎样装配模型

模型组件采用 Python 接口，配置文件引用已注册的组件及参数。以下为配置分工示意，字段尚未形成正式 schema。

```yaml
model:
  population: community_population_v1
  behaviors: community_behaviors_v1
  environment: shared_resources_v1
  activities: negotiation_and_cooperation_v1
  time_policy: discrete_events_v1
  visibility_policy: member_scoped_v1
  seed: 42

execution:
  pool: ray
  function_workers: 2
  maf_workers: 2
  model_endpoint: research_endpoint
  max_inflight_tasks: 16
  quota_profile: controlled_probe
  store_profile: local_postgres_and_blobs
  on_runtime_error: pause
```

初始化先展开群体与环境，再保存初始状态和事件。模型端点配置包含 provider、model、可用 revision、解码设置和凭据引用；凭据本身不进入运行清单。

提示、工具、记忆、时间和信息规则均保存版本。实际端点、硬件与预算由运行配置确定，示意中的 worker 数不构成性能承诺。

## 2. 运行操作

| 拟提供操作 | 用户看到的结果 |
|---|---|
| validate | 组件、schema、关系、时间及恢复能力检查 |
| start | run_id、定义摘要、初始状态与运行位置 |
| status | 当前坐标、提交版本、就绪/等待/执行任务及预算 |
| inspect actor / activity | 授权范围内的状态、成员、等待条件与来源 |
| pause / resume / stop | 明确的操作状态和可恢复位置 |
| check | 信息、资源、身份、提交与活动性质报告 |
| export / replay | 指定范围的记录及回放检查结果 |

操作入口先提供 Python 与 CLI，界面可以复用这些接口。平台多租户和复杂人机操作产品化在后续扩展，首版以单研究团队受控运行配置为边界。

运行状态区分 running、paused、quiescent、completed、failed 和 stopped。暂停请求处理中的 pausing 单独显示，避免把“已发送暂停请求”误报为“已安全暂停”。

## 3. 记录分为三类

| 记录 | 内容 | 保留规则 |
|---|---|---|
| 恢复与生效记录 | 任务输入、选中尝试、提交、状态、投递、checkpoint 引用 | 完整保存至相应恢复保留期结束 |
| 行为与因果记录 | 观察、调用响应、行动、反馈、消息来源与关联 | 需要复核行为的运行完整保留对应引用 |
| 运行诊断 | 日志、调用耗时、队列、worker 指标、调试细节 | 可配置采样与保留期 |

RunRecorder 使用 run_id、actor_id、activity_id、task_id、attempt_id、request_id、call_id 和 commit_id 关联这些记录。模拟坐标与墙钟时间分别保存。

完整的行为记录不要求保存模型未提供的内部推理；可保存实际请求、可见响应、结构化决策与外部工具结果。轨迹中的“该请求触发了该反馈”是执行关系，不能据此直接作经验因果效果判断。

## 4. 指标与诊断

| 维度 | 核心指标 | 回答的问题 |
|---|---|---|
| 持续规模 | 主体数、状态字节、未结束活动、等待索引 | 长期保存多少对象 |
| 工作吞吐 | 片段/秒、行动处置/秒、消息投递/秒 | 有效完成多少工作 |
| 延迟分解 | 排队、装载、行为、屏障、环境、提交耗时 | 慢在何处 |
| 模型使用 | 调用、token、预算预留、实际/估计费用、unknown | 成本如何形成 |
| 可靠性 | 重试、失效结果、重复投递、恢复耗时 | 失败是否被正确处置 |
| 模型结构 | 活跃率、通信密度、活动成员与重叠度 | 当前负载是什么 |

只报告 token 吞吐会遗漏共享环境和提交成本。负载报告同时列明硬件、worker、响应分布、状态体积和模型设置。

## 5. 系统检查与轨迹输出

检查器围绕八类性质工作：信息范围、状态归属、资源约束、活动生命周期、时间顺序、重复效果、接续完整性及账目一致。每项报告附关联身份和可定位记录。

通用轨迹首先服务调试、恢复与组件比较。后续 EPG 接口采用：

```text
通用过程记录 → 独立 EPG 适配器 → 事件图展示与领域分析
```

保存主体、活动、模拟时间、请求—反馈和提交关联即可为该适配提供基础。图的事件抽取粒度、领域词表和科学评价另行设计，不进入运行内核。

<a id="extensions"></a>

## 6. 外部协议怎样接入

| 需求 | 接入位置 | 合同要求 |
|---|---|---|
| 外部知识与工具服务 | MAF 工具 / MCP 适配 | 来源范围、结果记录、只读或副作用分类 |
| 远端 Agent | BehaviorExecutor 或活动参与者适配 | 身份绑定、可见输入、请求与响应、重试与恢复 |
| 人在环 | 运行控制与活动外部输入 | 注入内容、操作者与模拟坐标有记录 |
| 外部观察面板 | 只读状态与记录 API | 不直接改写模拟状态 |

协议适配可复用 MAF 生态，具体 A2A、MCP 或界面适配包在需要时核验。终态设计保留这些扩展位置，首版验收不要求把全部协议同时产品化。

内部主体高频通信采用 MessageRouter 合同。跨系统连接也通过相同的模拟身份和反馈边界生效，不能因成功连接远端服务而跳过这些规则。
