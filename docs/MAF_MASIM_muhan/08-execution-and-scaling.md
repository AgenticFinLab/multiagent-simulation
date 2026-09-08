# 08 · 分布式执行、规模与成本

[返回总览](README.md) · 前一篇：[时间与通信](07-time-and-communication.md) · 下一篇：[状态与恢复](09-state-and-recovery.md)

## 1. 执行路线与理由

参考实现采用 Python、MAF、Ray、PostgreSQL 和 BlobStore。一个 run 保持一个逻辑协调与提交顺序，行为与机制计算任务分配给有界共享 worker。多个独立 run 可以分别配置协调进程并共享模型端点配额。

这一路线复用 MASim 的 Ray 经验，同时使主体总数和实际计算资源分别扩展。代价是增加状态装载、接续重建与事务存储；单个 run 的共享环境和提交顺序仍可能限制扩展。

MAF 负责客户端、工具循环和局部工作流，Ray 负责执行进程及资源调度。模型推理服务作为端点接入，本系统管理它的使用方式，不承担训练或另建推理引擎。

## 2. 物理部署

```mermaid
flowchart TB
    subgraph COMPUTE["运行与计算"]
        USER["使用入口<br/>Python / CLI"]
        COORD["RunController<br/>每次运行一个协调进程"]
        subgraph RAY["Ray 集群 · 单机或多机"]
            WORKERS["共享 worker 池<br/>FunctionWorker：CPU 任务<br/>MAFWorker：模型与工作流"]
            QUOTA["ModelAccess<br/>端点配额与调用账目"]
        end
        COORD <-->|执行请求 / 执行结果| RAY
        WORKERS <-->|调用许可 / 用量结算| QUOTA
    end

    MODEL["外部模型与工具服务"]
    subgraph SUPPORT["共享持久化与观测"]
        direction LR
        DB["PostgreSQL<br/>事务状态与元数据"]
        BLOB["BlobStore<br/>检查点与大载荷"]
        REC["RunRecorder<br/>过程记录与指标"]
        DB ~~~ BLOB ~~~ REC
    end

    USER --> COORD
    WORKERS -->|MAF 客户端调用| MODEL
    COMPUTE -.->|按职责访问| SUPPORT
    QUOTA ~~~ SUPPORT
    MODEL ~~~ SUPPORT

    classDef control fill:#f1f5f9,stroke:#64748b,color:#1e293b
    classDef runtime fill:#e9f5f1,stroke:#438878,color:#174b40
    classDef state fill:#fff6e7,stroke:#b88a42,color:#664817
    class USER,COORD,MODEL control
    class WORKERS,QUOTA runtime
    class DB,BLOB,REC state
    style COMPUTE fill:#ffffff,stroke:#94a3b8
    style RAY fill:#f5faf8,stroke:#8eb8a9
    style SUPPORT fill:#fffcf5,stroke:#c9b182
```

虚线概括按职责访问：协调进程提交模拟状态，ModelAccess 写调用账目，worker 写候选载荷，RunRecorder 读取过程记录。数据库保存哪些对象见 [09](09-state-and-recovery.md)。

单机开发部署本地 Ray、PostgreSQL 与本地持久 BlobStore；多机部署沿用相同合同，BlobStore 必须能由所有执行节点读取。worker 本机临时目录和 Ray 对象存储都不作为恢复的唯一依据。

## 3. 资源对象与粒度

| 对象 | 承载位置 | 扩展单位 |
|---|---|---|
| 主体与子角色状态 | RunStore，按需缓存 | 对外主体数、内部角色数与热状态体积 |
| 活动、行为实例与等待 | RunStore + checkpoint 引用 | 未结束实例、成员、角色会话与待请求 |
| FunctionWorker | Ray 计算进程 | CPU 任务及简单行为批次 |
| MAFWorker | 有界异步 Ray Actor | 行为片段、机制任务及模型 I/O |
| 模型客户端 | worker 自己的事件循环 | 可复用连接，不共享可变会话 |
| ModelAccess | 端点级共享配额服务 | endpoint / quota group |
| 协调与后果处理 | 每 run 一个逻辑协调进程 | 独立运行，或未来有证据支持的内部优化 |

MAFWorker 使用显式并发上限；阻塞函数和 CPU 密集处理进入 FunctionWorker。Ray 异步 Actor 复用单个事件循环，阻塞操作会影响其他任务，因此需要测量实际的非阻塞路径。[Ray 异步 Actor](https://docs.ray.io/en/latest/ray-core/actors/async_api.html)

worker 按请求装载行为实例或机制输入，完成或进入持久等待后释放。流程工厂、客户端与不可变定义可以缓存，会话按实例、主体、角色和版本重建。内部角色也使用这套共享执行方式，无须常驻 Ray Actor；嵌套流程由 MAF 在局部执行。

## 4. 六项规模方法

| 方法 | 要降低的开销 | 保持的条件 |
|---|---|---|
| 事件定位与等待索引 | 大量未激活主体的空检查 | 激活集合和时间规则相同 |
| 有界派发与背压 | 无界任务、模型队列及结果堆积 | 当前阶段任务清单保持完整 |
| 简单行为批处理 | 细粒度 Ray 调度与 I/O | 每项任务身份、随机流和处置可单独恢复 |
| 版本化装载与热缓存 | 重复读库和构造成本 | 缓存键包含版本，不能读到未来状态 |
| 连接与模板复用 | 客户端握手、工厂初始化 | 活动和会话状态隔离 |
| 共享内容与批写记录 | 重复载荷、投递及写入成本 | 逻辑接收者和恢复记录仍完整 |

稀疏激活通过减少实际工作取得收益；密集交互与高争用负载仍可能受屏障或环境限制。目标是测清每种负载的主导成本，再调整对应层。

AgentSociety 2 的当前架构提供了状态重建、批次执行与共享服务的参考；它的 LLM 并发控制以进程为单位，本方案还需端点级总配额，不能直接把局部并发上限相加作为全局治理。[AgentSociety 2 架构](https://agentsociety2.readthedocs.io/en/latest/architecture.html)

<a id="model-binding"></a>

## 5. 模型绑定与调用管理

### 5.1 模型语义与连接配置

模型绑定规定使用什么模型及决策参数，端点绑定规定如何连接和分配调用额度。这样，扩充执行资源或更换连接时，可以单独核对模型是否保持一致。

| 配置 | 内容 | 变化的处理 |
|---|---|---|
| ModelBinding | provider 适配协议、模型身份、可用 revision、解码参数 | 纳入模型定义摘要，变化建立新运行定义 |
| 行为及机制定义 | 提示与渲染器、输出 schema、工具、模型绑定、调用策略 | 决定实际决策方法，保存版本 |
| EndpointBinding | ModelBinding 到 URL / deployment 的映射、凭据引用、连接参数与配额组 | 可独立调整，须保持所声明模型一致 |
| 实际调用证据 | 框架与 provider SDK 版本、请求参数、返回模型标识和核对状态 | 逐调用保存，恢复检查兼容性 |

同一父主体的子角色可以引用不同 ModelBinding；记忆和环境机制也显式绑定。运行层限流可以延迟或暂停调用，不能为降低成本静默改变温度、输出上限、提示或模型。

启动和恢复时核对实际端点与声明绑定。地址相同或 deployment 同名不足以证明模型相同；发现模型或可核对 revision 不符则停止相应运行。服务未提供 revision 或无法独立核对时，记录 declared_only 及可获得的标识，说明该模型版本仅有配置声明，尚未经独立核验。

更换 provider 适配或 SDK 可能改变请求、工具和输出行为，不能仅因 model 字符串相同就宣称等价。依赖变更需适配兼容检查；涉及模型语义变化时使用新的运行定义。

### 5.2 调用、配额与账目

```text
MAF 即将调用模型
  → 检查 run / task / attempt 是否仍有效
  → 申请端点并发许可和用量预留
  → worker 通过 MAF client 发出实际请求
  → 保存响应或错误
  → 结算用量并释放可确认的许可
```

配额包含端点总并发、请求速率、token 速率及每次运行的预算。调用账目关联运行、任务、尝试、call_id 和模型绑定，再记录所属主体、角色或机制组件，具体字段见 [10](10-operation-and-observability.md)。每次实际调用只计一次，按父主体汇总时避免重复累加子角色费用。

预算预留依据已知价格、输入估计和最大输出计算。价格未知或供应商未报告用量时，费用标注为估计值，不作精确费用保证。

MAF chat middleware 可覆盖工具循环中的各次模型调用，适合作为入口；SDK 内部重试应关闭或显式纳入统一策略。仅包围最外层 Agent 调用无法完整统计多步调用。[MAF Middleware](https://learn.microsoft.com/en-us/agent-framework/concepts/agents/middleware/)

采用一次逻辑配额所有者管理一个端点配额组，持久账目支持服务重建。失效 worker 和旧协调实例不能取得新调用许可。运行层重试有明确次数和退避，工具及业务层不能再叠加未登记的重试。

调用中断且结果未知时保留 unknown 账目，通过查询或明确的核对策略处置；外部请求可能仍在运行，租约到期不证明调用已经结束。恢复无法确认时暂停相应调度，避免无依据地释放全部预算再重复调用。

预算不足停止派发新调用，收集已在执行的结果。若本阶段不能完成，则保存部分阶段进度并暂停；恢复仍使用原任务清单与输入版本，详见 [09](09-state-and-recovery.md#pause)。

## 6. 执行优化与模型变化

| 调整 | 分类 | 检查方式 |
|---|---|---|
| worker 数、传输压缩、批写 | 执行优化 | 固定响应下状态与因果关系一致 |
| 确定性纯函数缓存 | 执行优化，前提是完整输入和版本相同 | 缓存与重算结果相同 |
| 固定运行响应回放 | 回放模式 | 严格匹配请求与保存响应 |
| 复用一次 LLM 输出给多个主体 | 模型变化 | 可能改变随机性与主体间相关性 |
| 语义缓存、摘要、反思频率 | 模型变化 | 记录信息变换并比较行为影响 |
| 主体聚合、代表者、活跃抽样 | 模型变化 | 保存成员映射与策略，对照未聚合模型 |
| 引入持久子角色或修改汇总、内部共享规则 | 模型变化 | 保存结构与信息规则，检查父主体行为的变化 |
| 低频 LLM 计划 + 高频规则执行 | 显式混合行为 | 计划有效期、更新触发和执行边界可查看 |
| 超时改用其他行为 | 显式故障模型 | 标记触发条件及对模拟的影响 |

模型作者通过配置选择这些方法，系统保存其版本与影响范围。机器负载只影响运行调度，不自动改变主体行为机制。

## 7. 怎样报告规模

至少同时报告 N（对外持续主体）、内部 SubAgent 数、A（活跃任务）、K（未结束活动）、未结束行为实例、活动成员数、消息密度、状态体积、模拟时长及端点吞吐。主体容量与单位墙钟时间完成的有效工作分别计量。

阶段模型调用量按行为、prepare、adjudicate 和重试分别统计。复合主体内部调用计入所属行为，不再以父子两级重复计算。实际成本取决于角色数、内部协作深度、上下文、输出长度及价格，总主体数不能单独决定预算。

单 run 的关键风险是慢任务屏障、共享环境热点、串行提交与数据装载。未来若要在一个 run 内分区推进，需证明跨区因果和冲突规则，不能仅以更换队列替代这项设计工作。
