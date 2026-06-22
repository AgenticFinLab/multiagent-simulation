# MASim 项目结构

## 1. 项目定位

MASim 是一个面向金融市场与群体行为研究的多智能体模拟框架。它让不同类型的 Agent 在共享市场中持续感知、决策、行动和通信，用于观察个体行为如何形成价格、成交量、波动率、流动性和信息传播等宏观结果。

仓库当前包含：

- 45 个正式场景；
- `Rule`、`LLM`、`RuleLLM`、`Rag` 四种决策机制；
- 180 套标准实验及对应分析结果；
- 261 个场景级角色，归并为 29 类通用 Agent 原型；
- Streamlit 实验回放与分析界面。

## 2. 核心执行链

```text
YAML 配置
  -> GeneralSimulator 创建 Ray Actor
  -> PlayerPersona 托管 Player 与基础设施代理
  -> Player 执行 perceive -> decide -> act
  -> Communication/Proxy 路由 Agent 消息
  -> Storage 保存逐轮状态和通信记录
  -> analysis.py 计算指标并生成分析产物
```

每轮模拟按拓扑层级执行四个阶段：

1. `execute`：同层 Agent 并行决策；
2. `collect`：收集行动与待发送信息；
3. `dispatch`：按拓扑发送信息；
4. `record`：持久化轮次、消息和市场状态。

## 3. 顶层目录

```text
multiagent-simulation/
|-- masim/                    # 通用模拟框架
|-- examples/                 # 场景实现与运行入口（含 examples/AGENT_POOL/ Agent 原型库与头像）
|-- configs/                  # 场景运行配置
|-- scripts/                  # 矩阵运行、预检和回归测试
|-- docs/                     # 架构、场景和实验规范
|-- simulation-results/       # 标准化 Simulation-180 结果包
|-- investment-agents/        # 场景级 Agent 角色档案
|-- setup.py                  # Python 包配置
`-- requirements.txt          # 项目依赖
```

## 4. 框架模块

| 模块                  | 职责                                 | 主要入口                           |
|-----------------------|--------------------------------------|------------------------------------|
| `masim/simulator`     | 加载配置、管理轮次、拓扑和 Ray Actor | `GeneralSimulator`                 |
| `masim/player`        | Agent 的感知、决策和行动逻辑         | `GeneralPlayer`                    |
| `masim/persona`       | 将 Player 包装为 Ray Actor           | `PlayerPersona`                    |
| `masim/communication` | 消息编码、解码和传输                 | `GeneralCommunicationChannel`      |
| `masim/proxy`         | 通信、存储、监控和资源代理           | `SendReceiveProxy`、`StorageProxy` |
| `masim/knowledge`     | 文档加载、向量索引和 RAG 检索        | `KnowledgeManager`                 |
| `masim/evaluation`    | 金融指标、有效性验证和可视化         | `finance/*`                        |
| `masim/interface`     | Streamlit 场景选择、回放和分析       | `app.py`                           |
| `masim/utils`         | 配置、拓扑、Ray 和结果读取工具       | `load_config`、`load_results`      |

职责边界：场景开发主要修改 `examples/` 和 `configs/`；`masim/` 应保持领域无关，不应写入某个金融场景的专用规则。

## 5. 场景与机制

一个正式场景通常具有四种实现：

| 机制      | 决策方式                             |
|-----------|--------------------------------------|
| `Rule`    | 纯规则，通常稳定且可重复             |
| `LLM`     | 大模型根据市场状态直接决策           |
| `RuleLLM` | 在显式规则和输出契约约束下调用大模型 |
| `Rag`     | 在 LLM 决策前检索论文或知识库        |

目录采用相同的二级结构：

```text
examples/{Scenario}/{Mechanism}/
|-- players.py        # 市场与投资者实现
|-- prompts.py        # LLM 提示词，Rule 模式可能没有
|-- run_*.py          # 单实验入口
|-- analysis.py       # 结果分析
|-- explain.md        # 机制与实现说明
`-- analysis.md       # 指标说明

configs/{Scenario}/{Mechanism}/
|-- simulation.yml    # 总入口、轮数、Ray、日志和输出路径
|-- players.yml       # Agent 类、角色、参数和模型配置
|-- persona.yml       # 存储、监控、通信和资源代理配置
`-- topology.yml      # Agent 间的有向通信关系
```

`simulation.yml` 通过 `!include` 引用其余配置。`players.yml` 中的 `class` 指向 `examples` 内的 Python 类，因此配置目录和实现目录必须同步修改。

## 6. 消息与状态

框架使用三层消息模型：

| 层      | 数据类型    | 含义                             |
|---------|-------------|----------------------------------|
| Player  | `Info`      | Agent 产生或消费的业务内容       |
| Proxy   | `Message`   | 加入发送者、接收者、时间和优先级 |
| Channel | `SimPacket` | 可记录和传输的编码消息           |

所有节点都是 Player。市场通过 `role: coordinator` 表达协调职责，普通投资者使用 `role: player`；执行先后和通信方向由 `topology.yml` 决定，而不是由角色类型硬编码。

## 7. 实验产物

直接运行场景后，产物通常写入：

```text
EXPERIMENT/{Scenario}/{Mechanism}/
|-- records/          # 每个 Agent 的逐轮决策和批量时间序列
|-- communication/    # 原始通信记录
|-- monitoring/       # 运行监控
|-- checkpoints/      # 可选检查点
|-- logs/             # 运行日志
`-- analysis/         # summary.json 与分析图
```

推荐通过 `masim.utils.load_results()` 读取结果，不要直接依赖底层 `batch_block_*.json` 和 `turn_block_*.json` 的存储细节。

`simulation-results/` 是整理后的发布数据包，不等同于本地运行产生的 `EXPERIMENT/`。它包含 180 套实验的配置快照、摘要、质量记录和聚合指标。

## 8. 运行入口

单个实验：

```powershell
python examples/Volmageddon/RuleLLM/run_volmageddon_rulellm.py `
  -c configs/Volmageddon/RuleLLM/simulation.yml
```

矩阵发现、隔离运行和超时管理：

```powershell
python scripts/run_example_matrix.py --dry-run `
  --scenario Volmageddon --mechanism RuleLLM `
  --isolated-artifacts --conda-bin conda --conda-env LMSim
```

Web 界面：

```powershell
streamlit run masim/interface/app.py
```

LLM 模式通常需要 `ARK_API_KEY`；RAG 还可能需要 `HUNYUAN_API_KEY`、`MINERU_API_KEY` 及可用的知识库目录。

## 9. 测试与验收

正式运行前执行：

```powershell
python scripts/test_scenario_contracts.py
python scripts/test_run_example_matrix.py
python scripts/test_run_api_full_plan.py
```

推荐流程：

```text
静态契约测试
  -> 单行 dry-run
  -> 单个完整轮次实验
  -> analysis.py
  -> 结构与数值质量检查
  -> 小批量或全量矩阵
```

验收分为三个层次：

1. 运行成功：进程完成全部配置轮次；
2. 结构成功：记录完整，无致命错误或大量解析回退；
3. 场景有效：市场结果确实复现目标机制。

进程返回 `SUCCESS` 不代表场景有效。完整预检规范见 `docs/experiment-preflight-skill/`，已有场景的修复规范见 `docs/example-revision-guide/`。

## 10. 常用定位

| 需求               | 首先查看                                                     |
|--------------------|--------------------------------------------------------------|
| 修改 Agent 行为    | `examples/{Scenario}/{Mechanism}/players.py`                 |
| 修改 LLM 输出      | `prompts.py`、解析器和 `players.yml`                         |
| 修改轮数或输出路径 | `simulation.yml`                                             |
| 增删 Agent 或参数  | `players.yml`                                                |
| 修改通信关系       | `topology.yml`                                               |
| 修改记录行为       | `persona.yml`                                                |
| 分析实验结果       | `analysis.py`、`masim/evaluation/`                           |
| 批量运行实验       | `scripts/run_example_matrix.py`                              |
| 排查实验失败       | `docs/example-revision-guide/08-runtime-failure-patterns.md` |
