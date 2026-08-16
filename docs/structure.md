# MASim 项目结构

## 1. 项目定位

MASim 是一个面向金融市场与群体行为研究的多智能体模拟框架。它让不同类型的 Agent 在共享市场中持续感知、决策、行动和通信，用于观察个体行为如何形成价格、成交量、波动率、流动性和信息传播等宏观结果。在项目的研究脉络中，MASim 同时承担两个角色：

1. 作为 **场景实验平台**，复现并分析已知的金融现象（泡沫、崩盘、行为偏差、流动性危机等）；
2. 作为 **Financial Multi-Agent World Model 的基座**，为新场景的快速构建提供标准化的 Agent / Market / Communication / Storage 抽象。

仓库当前包含：

- 45 个正式场景（见 `examples/{Scenario}/`），每个场景四种变体；
- 四种决策机制：`Rule`、`LLM`、`RuleLLM`、`Rag`；
- 标准化实验产物（`EXPERIMENT/` 单次运行 + `simulation-results/` 发布包）；
- 由 261 个场景级角色合并而来的 29 类通用 Agent 原型，外加 `masim/agents/defines/` 下的可复用 Agent 档案库；
- Streamlit 实验回放与分析界面；
- 每个新场景都以一份**用户/上游 LLM 撰写的目标说明文件** `{domain}-{scenario}.md` 作为唯一上游输入（格式由 `define-simulation-scenario-skill.md` 约束）；
- 位于 `masim/skills/` 的**设计 / 创建 / 升级** Skill 体系（`define-simulation-scenario-skill.md`、`agent-design-skill.md`、`implement-simulation-skill/`；两条顶层 pipeline：`create-simulation-pipeline.md` 从零新建、`polish-simulation-pipeline.md` 对已存在场景标准化升级）。

## 2. 核心执行链

```text
YAML 配置
  -> GeneralSimulator 创建 Ray Actor
  -> PlayerPersona 托管 Player 与基础设施代理
  -> Player 执行 perceive -> decide -> act (-> on_fill)
  -> Communication/Proxy 路由 Agent 消息
  -> Storage 保存逐轮状态和通信记录
  -> analysis.py 计算指标并生成分析产物
```

每轮模拟按拓扑层级执行四个阶段：

1. `execute`：同层 Agent 并行决策；
2. `collect`：收集行动与待发送信息；
3. `dispatch`：按拓扑发送信息；
4. `record`：持久化轮次、消息和市场状态。

**Player 生命周期细化**：金融场景 Player 由 `CanonicalRulePlayer` / `CanonicalLLMPlayer` / `CanonicalRagPlayer` / `CanonicalMarketCoordinator`（`masim/agents/_base.py`）派生。每一轮 `perceive → decide → act` 的最后一步由框架实现的 `_apply_fill_and_emit_action` 统一执行：从 `decide()` 返回的 `decision_payload` 中读取 `action / quantity / bid_price`，走 `require_positive_bid_price` 断言、`clip_order_to_liquidity`、更新 `cash / position`，然后调用可选的 `on_fill(action, quantity, bid_price)` 钩子进行 archetype 级 VWAP/cost-basis 更新。所有 archetype 类（含四个变体的 `players.py`）**禁止** override `act()` / `decide()`；如需 per-fill 状态维护，只能覆盖 `on_fill`。完整契约见 `docs/framework-contract.md`。

## 3. 顶层目录

```text
multiagent-simulation/
|-- masim/                    # 通用模拟框架 + 设计 Skill
|   |-- agents/              # 209 个 archetype .py + defines/ 行为规格
|   |   |-- _base.py  _coordinator_base.py  _rag_base.py
|   |   |-- finance/         # 195 个金融 investor agent (snake_case .py)
|   |   |-- market/          # 9 个 market coordinator (snake_case .py)
|   |   |-- opinion/         # 5 个 opinion agent (snake_case .py)
|   |   `-- defines/         # 可复用 Agent 行为规格档案库（与上面 1:1 镜像）
|   |       |-- finance/     # 195 个金融 agent 档案 (kebab-case .md)
|   |       |-- market/      # 9 个 market coordinator 档案
|   |       |-- opinion/     # 5 个 opinion-propagation 档案
|   |       `-- agent_images/ # 图标 PNGs + Streamlit Agent Market 资产
|   |-- communication/  evaluation/  format/
|   |-- integrations/event_process/ # G3 通用事件过程值、reducer、transport、trace 与 seal
|   |-- interface/  knowledge/  persona/  player/
|   |-- proxy/  simulator/  utils/ # simulator/phased.py 提供 opt-in phased lifecycle
|   `-- skills/               # define-simulation-scenario-skill.md, agent-design-skill.md, implement-simulation-skill/, create-simulation-pipeline.md (从零新建), polish-simulation-pipeline.md (升级已有)
|-- examples/                 # 标准/既有 MASim 场景实现与运行入口
|   |-- {Scenario}/           # 45 个正式场景（Rule/LLM/RuleLLM/Rag 四变体）
|   |-- CUSTOMIZED_SIMULATION/  # 自定义/未发布场景的工作空间
|   |-- document-sources/     # RAG 文档原料
|   `-- __init__.py
|-- configs/                  # 标准/既有 MASim 场景配置（与 examples/ 同名目录）
|-- projects/                 # 跨场景研究项目；可组合合同、评估器与多事件协议
|   `-- h2epr/                # H2EPR 事件过程模拟的项目根
|       |-- contracts/v1/     # 稳定的 Phase-0 合同接口
|       |-- decisions/        # 项目级、可演进的架构决策
|       |-- configs/          # H2EPR canary 配置；不与标准 configs/ 混用
|       |-- src/h2epr/        # 按职责扩展的 repository-local 研究实现（不由根包分发）
|       |   |-- construction/ # 显式输入适配和 typed Construction IR
|       |   |-- artifacts/    # EntityRegistry、roster 与 ParticipantArtifact 装配
|       |   |-- policies/     # 声明式 Rule policy/skill 输入（不执行）
|       |   |-- world/        # 归一化 canary 状态与纯计算 helper
|       |   |-- bundles/      # sealed construction / EventBundle 编译（不运行）
|       |   |-- runtime/      # G3 adapter、Rule policy、detector、reducer/runner
|       |   `-- compiler/     # G4 sealed-trace 校验与确定性 Generated EPG 编译
|       |-- tests/            # 分阶段 owning tests；tracked fixtures 仅保留 synthetic 输入
|       |-- README.md         # 项目入口和当前能力边界
|       |-- ARCHITECTURE.md   # 科学边界和候选扩展点
|       `-- EVOLUTION.md      # 合同版本与实现演进策略
|-- docs/                     # 架构、场景、实验规范与历史报告
|-- EXPERIMENT/               # 本地实验产物（运行时生成）
|-- simulation-results/       # 标准化发布数据包（外部交付）
|-- third-part/  tests/  build/
|-- setup.py
`-- requirements.txt          # 项目依赖
```

> `investment-agents/` 是历史遗留目录，新档案统一写入 `masim/agents/defines/<domain>/`。

`examples/` / 顶层 `configs/` 是当前标准 MASim 单场景约定；`projects/` 面向需要
跨场景合同、编译器、评估器和研究协议的长期研究项目。H2EPR 在
`projects/h2epr/` 公开稳定 V1 合同，并按职责容纳 construction、artifact、bundle
和 runtime 等项目专用实现；当前工程基线已覆盖 G1/G2、G3 Rule-runtime canary，
以及从 sealed trace 到 V1 Generated EPG/GraphSeal 的 Reference-blind G4 编译。
项目专用 `h2epr` 包不由根 `setup.py` 分发；G3 仅把领域无关的 phased/event-process 机制放入
`masim/`，事件身份、规则和配置仍留在项目根。该 canary 已跑通确定性执行链，
G4 则在项目根中消费经验证的 sealed trace，不改变 MASim 的默认运行路径；二者
都不代表 Reference 对齐、历史校准或 scientific readiness。后续场景、评估器和测试仍可在 Gate
证据与 ADR 指导下演进；对应目录只随实际实现创建，不使用空占位目录，当前边界
也不锁死最终目录或类名。
H2EPR 的冻结输入保留在
`data/h2epr/`，开发生成物进入被忽略的 `EXPERIMENT/H2EPR/` 或本地证据根；
tracked test tree 只接收最小 synthetic fixtures。经过单独筛选的发布包才进入
`simulation-results/H2EPR/`；输入、项目装配、运行工作区和发布边界不得混用。

## 4. 框架模块

| 模块                  | 职责                                 | 主要入口                                                                                                                                     |
|-----------------------|--------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------|
| `masim/simulator`     | 加载配置、管理轮次、拓扑和 Ray Actor；每个 `{V}Simulator` 与其配对的 `{V}SimulationRunner` + 模块级 `run()` CLI 便捷函数**同文件共存**（新模式按同一模板扩展） | `GeneralSimulator` / `GeneralSimulationRunner` / `run(scenario, default_config, ...)` / `BaseSimulationRunner`                                |
| `masim/integrations`  | 可选、领域无关的集成机制；G3 event-process 值、reducer authority、transport、trace 与 seals | `event_process/*` |
| `masim/player`        | Agent 感知/决策/行动的通用基类       | `GeneralPlayer`                                                                                                                              |
| `masim/agents`        | 金融场景 canonical 基类 + 29 个 archetype | `CanonicalRulePlayer` / `CanonicalLLMPlayer` / `CanonicalRagPlayer` / `CanonicalMarketCoordinator` / `_apply_fill_and_emit_action` / `on_fill` |
| `masim/persona`       | 将 Player 包装为 Ray Actor           | `PlayerPersona`                                                                                                                              |
| `masim/communication` | 消息编码、解码和传输                 | `GeneralCommunicationChannel`                                                                                                                |
| `masim/proxy`         | 通信、存储、监控和资源代理           | `SendReceiveProxy`、`StorageProxy`                                                                                                           |
| `masim/knowledge`     | 文档加载、向量索引和 RAG 检索        | `KnowledgeManager`                                                                                                                           |
| `masim/evaluation`    | 金融指标、有效性验证和可视化         | `finance/*`                                                                                                                                  |
| `masim/format`        | 通用 prompt / 订单 schema / 订单最终化 | `order.py`、`base_prompts.py`、`finalize.py` (`require_positive_bid_price` / `clip_order_to_liquidity`)                                       |
| `masim/interface`     | Streamlit 场景选择、回放和分析       | `app.py`                                                                                                                                     |
| `masim/utils`         | 配置、拓扑、Ray 和结果读取工具       | `load_config`、`load_results`                                                                                                                |
| `masim/skills`        | 设计/创建 Skill 体系                 | 见 §11                                                                                                                                       |

职责边界：标准 MASim 场景开发主要修改 `examples/` 和顶层 `configs/`。H2EPR 保持
独立研究项目根；ADR-0003 已依据 G1/G2 证据采用“通用 event-process 机制进入
`masim/`、H2EPR runtime/config 留在项目根”的 G3 可演进边界。
`masim/` 应保持领域无关，不应写入某个金融场景或某个 H2EPR 事件的专用规则；
`masim/skills/` 不参与运行时，只供设计阶段调用。

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
examples/{Scenario}/
|-- __init__.py
|-- {domain}-{scenario}.md  # 用户/上游 LLM 撰写的目标说明（上游输入；锁定后不可改）
|-- simulation-build-log.md    # 流水线生成的构建日志（AGENT_POOL 门、研究笔记、待解问题）
|-- simulation-bases.md     # 9 节理论与设计基线（变体共享）
|-- analysis-bases.md       # 7 节分析方法学基线（变体共享）
`-- {Mechanism}/            # 是否包含取决于目标文件 §10.1 的 build matrix
    |-- players.py        # 市场与投资者实现
    |-- prompts.py        # LLM 提示词，Rule 模式可能没有
    |-- run_*.py          # 单实验入口（thin shim → masim.simulator.general.run）
    |-- analysis.py       # 结果分析（Rule 为权威实现，其余继承）
    |-- explain.md        # 机制与实现说明（引用 simulation-bases.md §N.M）
    `-- analysis.md       # 指标说明（引用 analysis-bases.md §N.M）

configs/{Scenario}/{Mechanism}/
|-- simulation.yml    # 总入口、轮数、Ray、日志和输出路径
|-- players.yml       # Agent 类、角色、参数和模型配置
|-- persona.yml       # 存储、监控、通信和资源代理配置
`-- topology.yml      # Agent 间的有向通信关系
```

`simulation.yml` 通过 `!include` 引用其余配置。`players.yml` 中的 `class` 指向 `examples/` 内的 Python 类，因此配置目录和实现目录必须同步修改。

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

Web 界面：

```powershell
streamlit run masim/interface/app.py
```

LLM 模式通常需要 `ARK_API_KEY`；RAG 还可能需要 `HUNYUAN_API_KEY`、`MINERU_API_KEY` 及可用的知识库目录。

## 9. 测试与验收

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

## 10. Agent 档案与 Pool 复用

`masim/agents/defines/` 是 **可复用 Agent 档案库**，所有新场景都必须先经此目录做"复用 vs. 新建"判定，避免重复设计相同行为的 Agent。

```text
masim/agents/defines/
|-- finance/                            # 195 个金融领域 Agent 档案（momentum / fundamental / liquidity / ...）
|-- market/                             # 9 个 market coordinator 档案（price-impact / depeg / ...）
|-- opinion/                            # 5 个 opinion-propagation 档案（distorting / fact-check / ...）
|-- agent_images/                       # 头像图标 (icons/) 与设计说明 (design.md)
`-- README.md
```

- 单个 Agent 档案严格遵循 `masim/skills/agent-design-skill.md` 的 11 节格式；
- 文件名采用 kebab-case（如 `momentum-trader.md`、`fundamental-analyst.md`），与 H1 一致；
- 领域子目录（`finance/`、`market/`、`opinion/`，未来可能的 `epidemics/` 等）由档案的真实领域决定；
- 每个 `.md` 档案与 `masim/agents/<domain>/` 下的同名（snake_case）`.py` 实现构成 **1:1 镜像映射**（如 `defines/finance/momentum-trader.md` ↔ `agents/finance/momentum_trader.py`）；新增 Agent 必须同时添加 `.md` 规格和 `.py` 实现；
- 添加新 Agent 之前，必须先按 `masim/skills/create-simulation-pipeline.md`（新建场景时）或 `masim/skills/polish-simulation-pipeline.md`（升级已有场景时）的三段式匹配流程检索是否已有满足要求的档案。

未发布或试验性的自定义场景写入 `examples/CUSTOMIZED_SIMULATION/`，构成熟稳定后再迁入 `examples/<Scenario>/`。

## 11. 设计 Skill 体系

`masim/skills/` 是项目的"创建/升级手册"，**不参与运行时**，只在设计阶段被调用：

```text
masim/skills/
|-- define-simulation-scenario-skill.md   # 上游目标文件 {domain}-{scenario}.md 的格式规范（用户/LLM 撰写）
|-- agent-design-skill.md                 # 单 Agent 设计规范（领域无关，11 节）
|-- implement-simulation-skill/           # 单场景的分步方法学（Step 0 - Step 10 子技能库）
|   |-- 00-overview.md
|   |-- 01-mandatory-structure.md
|   |-- 02-root-documents-spec.md
|   |-- 03-variant-documents-spec.md
|   |-- 04-step0-load-target.md
|   |-- 05-step1-research.md
|   |-- 06-step2-agent-design.md
|   |-- 07-step3-config.md
|   |-- 08-step4-implement.md
|   |-- 09-step5-to-10-review.md
|   `-- 15-reference-assetbubble.md
|-- create-simulation-pipeline.md         # 顶层 pipeline #1：从零新建场景（目标文件 → 全套 artefact）
`-- polish-simulation-pipeline.md         # 顶层 pipeline #2：升级已有场景到当前 skill 基线（审计 + 补丁）
```

两条 pipeline 使用同一套子技能（`define-`、`agent-design-`、`implement-`），
入口不同，流程差异也不同：`create-` 是**构造流程**（从空目录构建全套 artefact），
`polish-` 是**审计-补丁流程**（对已存在 artefact 做结构对齐、handbook 校验、AGENT_POOL 重新匹配）。

调用关系 A：从零新建场景（`create-simulation-pipeline.md`）

```text
用户 / 上游 LLM
        |
        |-- 依据 define-simulation-scenario-skill.md 撰写
        v
examples/{Scenario}/{domain}-{scenario}.md   (Status: draft)
        |
        v
create-simulation-pipeline.md          (pipeline #1 入口)
        |
        |-- Phase 0: 读取并验证目标文件 + §11 校验 ----> examples/{Scenario}/simulation-build-log.md
        |           (校验通过后将目标文件 Status: draft -> locked)
        |-- Phase 1: 文献研究（验证/扩展目标 §4-§6-§9）
        |-- Phase 2: Agent 角色规划（基于目标 §7）
        |-- Phase 3: AGENT_POOL 复用门
        |        |-- 复用现有 agent (masim/agents/defines/<domain>/*.md)
        |        `-- 新建：调用 agent-design-skill.md + 三遍 §6 checklist
        |              ----> 写入 masim/agents/defines/<domain>/<kebab>.md
        |-- Phase 4: 切换到 implement-simulation-skill/ 的 02 -> 08，完成 simulation-bases / configs / players.py
        `-- Phase 5/6: 三遍场景级审查 + 实验执行
              (闭包时将目标文件与 simulation-build-log.md 一并 released)
```

调用关系 B：升级已有场景（`polish-simulation-pipeline.md`）

```text
现有 examples/{Scenario}/                (已有 simulation-bases.md、analysis-bases.md、Rule/、LLM/ 等)
        |
        v
polish-simulation-pipeline.md          (pipeline #2 入口)
        |
        |-- Phase A: 现状盘点，生成 gap list（工作区暂存，不入库）
        |-- Phase B: 若缺失目标文件则反向工程 {domain}-{scenario}.md
        |           (§11 三-PASS → Status: locked)
        |-- Phase C: 根文档审计（simulation-bases.md / analysis-bases.md
        |             vs implement-simulation-skill/02-root-documents-spec.md）
        |-- Phase D: 每个 agent 审计（handbook §3.1-§3.11 + AGENT_POOL 三段式重跑）
        |           每个 agent 通过三遍 handbook §6 才算过关
        |-- Phase E: 每个 variant artefact 审计（explain.md / analysis.md / players.py / *.yml）
        |-- Phase F: 场景级三遍审查（复用 09-step5-to-10-review.md）
        `-- Phase G: 每个 variant smoke test → 目标文件 §0 CHANGELOG 追加一行 → Status: released
              审计痕迹：目标文件 §0 CHANGELOG + agent §3.11 Provenance + git commit history
              （**不生成** simulation-build-log.md）
```

## 12. 常用定位

| 需求               | 首先查看                                                          |
|--------------------|-------------------------------------------------------------------|
| 修改 Agent 行为    | `examples/{Scenario}/{Mechanism}/players.py`                      |
| 修改 LLM 输出      | `prompts.py`、解析器和 `players.yml`                              |
| 修改轮数或输出路径 | `simulation.yml`                                                  |
| 增删 Agent 或参数  | `players.yml`                                                     |
| 修改通信关系       | `topology.yml`                                                    |
| 修改记录行为       | `persona.yml`                                                     |
| 分析实验结果       | `analysis.py`、`masim/evaluation/`                                |
| 排查实验失败       | `docs/example-revision-guide/08-runtime-failure-patterns.md`      |
| 理解框架契约（act/decide/on_fill 边界） | `docs/framework-contract.md`（唯一权威）                    |
| 审计场景是否违反契约 | `scripts/audit_scenario_contract.py --scenario {Scenario}`     |
| 撰写新场景目标文件     | `masim/skills/define-simulation-scenario-skill.md`（{domain}-{scenario}.md 规范）    |
| 从零创建新场景         | `masim/skills/create-simulation-pipeline.md`（pipeline #1；需先有目标文件）           |
| 升级已有场景到最新规范 | `masim/skills/polish-simulation-pipeline.md`（pipeline #2；对 examples/ 下已有场景做审计-补丁） |
| 设计新 Agent       | `masim/skills/agent-design-skill.md` + `masim/agents/defines/`     |
| 查找可复用 Agent   | `masim/agents/defines/<domain>/`，按文件名/Summary/全文三段式检索  |
