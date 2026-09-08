# 11 · MASim 迁移与工程组织

[返回总览](README.md) · 前一篇：[使用与观测](10-operation-and-observability.md) · 下一篇：[实施与验收](12-implementation-and-acceptance.md)

## 1. 迁移原则

以新系统职责为单位迁移 MASim 的通用资产：复用仍适用的机制、代码和测试，改写与主体常驻进程、固定轮次及领域副作用耦合的部分。原仓库保持既有实现，新项目通过来源记录追溯迁移。

下表所列资产基于 [MASim 源码 cbe507e8](https://github.com/AgenticFinLab/multiagent-simulation/tree/cbe507e814bf8e4742fc6c527441a21ece10f269)。迁移时逐项核对实际来源提交和许可证。

## 2. 资产怎样迁入

| MASim 资产 | 可保留内容 | 新系统位置与必要改动 |
|---|---|---|
| [Player](../../masim/player/general.py)、[Persona](../../masim/persona/general.py) | 身份、行为生命周期和配置经验 | model / runtime；将持久主体状态与执行实例分开 |
| [GeneralSimulator](../../masim/simulator/general.py) | 并行执行、收集与 Ray 组织经验 | coordination / execution；按事件和活动片段重组 |
| [TopologyGraph](../../masim/utils/topology.py) | 图关系、连接和分组计算 | 关系与路由组件；执行拓扑不直接等同于模拟时间 |
| [Proxy](../../masim/proxy/general.py) 与通信分层 | 内容、路由和传输信封分离 | MessageRouter；补充 activity_id、可见时间与投递身份 |
| [配置](../../masim/utils/config.py)、[schema](../../masim/simulator/config_schema.py) | 组件引用、模板和类型检查 | ModelRegistry；区分模型与执行配置，统一版本 |
| [History](../../masim/utils/history.py)、[ResumeScanner](../../masim/simulator/resume_scanner.py) | 缓存、批写和进度识别 | storage / observability；补充联合状态、任务和消息恢复 |
| [LLM helper](../../masim/utils/llm_utils.py) | 错误分类与调用经验 | MAF / ModelAccess；统一重试，检查同步阻塞与默认回退 |
| 领域 Player、撮合、填单逻辑 | 仍适用的领域规则 | 可选 examples / plugins；按环境和行为职责分别适配 |
| 既有测试 | 对保留机制有约束力的断言 | 对应组件测试；重新验证新合同，保留迁移说明 |

通用启动路径目前为每个 Player 创建 Ray Persona；`run()` 的轮次接续说明主体 custom_state 从配置重建。因此现有机制为新系统提供工程基础，完整状态恢复与主体承载方式仍需要实质改造。[对应源码](../../masim/simulator/general.py)

同样，领域 `on_fill` 的后果处理经验可以迁移，具体金融语义由领域组件保留。新系统不要求所有主体都经过交易者或市场对象的继承层次。

## 3. 新项目的包结构

以下为目标包结构，`sim_runtime` 为暂定包名。

```text
src/sim_runtime/
  contracts/                 # 定义、身份、请求、结果、版本与 schema
  model/                     # 注册、群体初始化、组合校验
  coordination/              # Scheduler、ActivityManager、MessageRouter
  environment/               # ObservationBuilder、环境与后果处理接口
  runtime/
    function.py              # 函数和状态机
    maf/                     # MAFExecutor、WorkflowBridge、会话与工具
  execution/                 # Ray worker 池、任务尝试、ModelAccess
  storage/                   # RunStore、事务、BlobStore、恢复与迁移
  observability/             # 记录、指标、检查、回放与导出
  cli.py                     # 运行管理入口

examples/
  resource_community/        # X / Y 贯穿示例
  component_extension/      # 新行为、新环境、新活动的接入示例
tests/
  contracts/
  integration/
  recovery/
workloads/                   # 负载定义、响应分布与测量配置
docs/                        # 架构、组件开发、运行、证据与限制
```

按模块职责拆包，避免把全部机制堆入一个 simulator 类。初期实现可以很小，但名称和数据流与最终设计一致。

## 4. 依赖边界

| 层 | 允许依赖 | 边界 |
|---|---|---|
| contracts | 基础类型与序列化库 | 无 MAF、Ray、数据库对象 |
| model / coordination | contracts、组件接口 | 不直接调用模型 SDK |
| environment | contracts、领域算法 | 不写数据库、不隐藏模型调用 |
| runtime/maf | contracts、固定版本 MAF | 不直接修改生效状态 |
| execution | contracts、运行适配、Ray | 不解释领域行动后果 |
| storage | contracts、数据库与 Blob 客户端 | 不执行主体行为 |
| examples / plugins | 公开扩展接口 | 不靠改写通用协调代码接入 |

连接池、协程、锁和 Ray 对象引用均不进入持久数据。运行服务通过明确接口注入，组件可以在受控条件下替换和独立检查。

## 5. 依赖锁定与迁移记录

MAF 接口参考 core 1.17.0、orchestrations 1.1.1。实现时统一锁定 Python、MAF 包、provider、Ray、存储驱动及序列化依赖，并保存实际包和源码摘要。

每项迁移记录来源路径与提交、迁入位置、保留行为、修改原因、依赖、测试和结果。新旧状态格式之间的迁移也使用版本号及验证记录。

开发文档中的接口和样例在实现时纳入检查。某个适配因依赖版本而变化，应同步更新该适配合同和验收证据，通用合同保持可控演进。

## 6. 工程交付内容

工程交付包含实现代码、组件合同、依赖锁、迁移来源、运行与扩展示例、测试及负载报告。架构说明应与实际接口保持一致，报告明确列出已验证能力、未覆盖项和已知限制。验收要求见 [12 · 实施与验收](12-implementation-and-acceptance.md)。
