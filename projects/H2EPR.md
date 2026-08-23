# H2EPR 项目指南

本文介绍 H2EPR 在 `multiagent-simulation` 仓库中的位置、主要模块以及当前开发方向。第一次接触
项目时，可以先阅读本页，再根据需要进入 `projects/h2epr/` 中的详细文档。

## 项目概览

H2EPR 研究如何让多个参与者 Agent 从给定时间点出发，模拟真实社会事件的后续演化，并把整个过程
记录为可检查、可重放的事件轨迹。

项目目前位于：

```text
projects/h2epr/
```

这里包含 H2EPR 自己的合同、Agent 定义、事件配置、运行适配器和 EPG 编译器。MASim 提供通用的
多 Agent 执行基础，H2EPR 则负责真实事件研究所需的证据、制度、行为和评价语义。

项目已经跑通以下工程链路：

```text
事件材料
  -> Construction IR
  -> ParticipantArtifact / EventBundle
  -> Rule-based runtime
  -> sealed trace and replay
  -> Generated EPG
```

1907 年金融恐慌事件已经完成七份 Agent Definitions、五份 population models、Roster Definition
release v0.1、全 Roster consolidated mapping、Event Scenario Definition v0.1，以及非可执行的
Scenario Configuration v0.1。配置已固定机制覆盖用途、精确时间边界、16 actor / 10 unit assembly、
初始分类记录、结构基线、策略语义和敏感性边界。其最小静态 admission loader、独立的
KT–NBC–NYCH 四动作/三路由 bounded binding，以及五 tick 的 E7 negative conformance、确定性
trace/replay、review 与方法 closeout 均已完成。S0--S4 至此停止，不直接启动全事件模拟。

## 文档导航

| 文档 | 内容 |
|---|---|
| 本页 | 仓库结构、模块关系和开发方向 |
| [Research projects](README.md) | `projects/` 目录中的研究项目索引 |
| [H2EPR README](h2epr/README.md) | 已有功能、运行边界和测试入口 |
| [Event modeling workflow](h2epr/WORKFLOW.md) | 事件级阶段、门禁、停止边界和当前进度 |
| [Architecture](h2epr/ARCHITECTURE.md) | 数据流、运行职责和信息隔离 |
| [Evolution](h2epr/EVOLUTION.md) | 合同版本与内部实现的演进规则 |
| [Agent guide](h2epr/agents/README.md) | Agent Definition 的目录、命名和迭代方式 |
| [Contracts V1](h2epr/contracts/v1/README.md) | 稳定的机器接口和 schema |
| [Tests](h2epr/tests/README.md) | 各测试套件的运行方法 |

## 仓库布局

```text
multiagent-simulation/
├── masim/                     # MASim 通用框架
├── examples/                  # 标准 MASim 场景
├── configs/                   # 标准 MASim 场景配置
├── projects/
│   ├── README.md              # 研究项目索引
│   ├── H2EPR.md               # H2EPR 项目指南
│   └── h2epr/                 # H2EPR 项目根
├── data/h2epr/                # 冻结的事件输入
├── .local-runtime/            # 本地研究记录、工作稿和证据归档
├── EXPERIMENT/H2EPR/          # 本地运行输出
└── simulation-results/H2EPR/  # 经过筛选的发布结果
```

H2EPR 的源码和研究资产集中在 `projects/h2epr/`。根级 `examples/` 和 `configs/` 用于标准 MASim
场景，通常只作为组织方式的参考。`data/h2epr/` 保存输入材料，运行产生的文件进入实验目录。

## H2EPR 目录

```text
projects/h2epr/
├── WORKFLOW.md                 # 事件级标准化阶段与门禁
├── contracts/v1/             # 稳定合同和 JSON Schema
├── decisions/                # 架构决策记录
├── configs/                  # 配置指南、语义模板、已接受配置与冻结 canary
│   ├── scenario-configuration-template.md
│   ├── schemas/
│   └── panic_1907/
├── agents/
│   ├── agent-definition-template.md
│   └── defines/panic_1907/
├── populations/
│   ├── defines/panic_1907/
│   └── interfaces/panic_1907/
├── releases/panic_1907/      # 语义 release 清单与哈希
├── skills/
│   ├── event-agent-batch/
│   ├── historical-evidence-research/
│   ├── participant-behavior-research/
│   ├── agent-definition/
│   ├── agent-definition-review/
│   ├── event-scenario-design/
│   ├── roster-mapping-conformance/
│   └── scenario-configuration/
├── scenarios/
│   ├── scenario-definition-template.md
│   ├── scenario-interface-closure-template.md
│   └── panic_1907/
├── src/h2epr/
│   ├── construction/
│   ├── artifacts/
│   ├── policies/
│   ├── world/
│   ├── bundles/
│   ├── agents/
│   ├── configuration/
│   ├── runtime/
│   └── compiler/
└── tests/
```

### 模块职责

| 路径 | 用途 |
|---|---|
| `WORKFLOW.md` | 事件级阶段、授权门禁、关闭审计和当前进度 |
| `contracts/v1/` | Construction、runtime、trace、seal、Generated EPG 等机器接口 |
| `configs/` | 版本化 Scenario Configuration 与冻结工程 canary，二者不得互相提供默认值 |
| `construction/` | 加载明确授权的来源，并生成 typed、lossless Construction IR |
| `artifacts/` | EntityRegistry、provenance 和 ParticipantArtifact |
| `policies/` | 现有 Rule canary 使用的声明式策略 |
| `world/` | canary 世界状态和纯计算函数 |
| `bundles/` | Construction bundle、EventBundle 及其校验 |
| `agents/` | 当前 Agent Definition 研究资产、通用 binding 约束和冻结工程基线 |
| `populations/` | 无法或无需逐人重建的异质参与者群体模型及轻量接口检查 |
| `releases/` | 固定 Roster、Definitions、群体模型、证据、场景骨架和接口身份 |
| `scenarios/` | 事件场景模板、release 接口闭合、场景语义、环境策略和有界集成路径 |
| `runtime/` | H2EPR 的 MASim 适配、Rule runtime、detector 和 runner |
| `compiler/` | 校验 sealed trace，并生成 EPG 和 GraphSeal |
| `tests/` | 合同、construction、runtime、compiler 和 Agent 测试 |

`skills/` 覆盖证据与角色研究、Definition 编写和审核，以及 release 之后的
场景设计、consolidated mapping/conformance 和 Scenario Configuration。配置 Skill 已从首个
接受用例提炼，并把窄版工程 preflight 明确限制为后续静态配置准入；它仍需由第二事件前向检验。
每个 Skill 以 `SKILL.md` 作为入口，并把只在特定阶段需要的详细规范放在相邻 `references/` 中。

这些目录按职责组织。内部类名和文件拆分可以随着实现演进；`contracts/v1` 的公开语义保持稳定。

## 架构概览

```text
sources and evidence
  |
  v
Agent Definitions + scenario/environment
  |
  v
ParticipantArtifact / RuntimeScenarioBundle
  |
  v
actor-specific observation
  |
  v
Agent emits intent or message
  |
  v
environment adjudicates
  |
  v
authoritative reducer commits state
  |
  v
trace, seals and replay
  |
  v
Generated EPG
```

### 信息与状态

运行环境保存完整世界状态，并为每个 Agent 生成其当时可以获得的 observation。Agent 根据
observation 和自己的持久状态作出决定；状态变化由 reducer 统一提交。

这一区分对历史事件模拟很重要：模拟器知道某项事实，并不意味着事件参与者在当时也知道它。

### Agent 与环境

Agent 输出的是请求、提议、授权、拒绝或其他 intent。环境负责检查权限、资源和制度约束，并产生
执行、部分执行、延期、无效果或失败等结果。

因此，请求已发送、消息已送达和业务结果已发生是三个不同状态。trace 会保留它们之间的关系。

### Trace 与 EPG

runtime 将 observation、decision、intent、message、result 和 state transition 写入
hash-chained trace。每个 tick 和完整运行都有 seal，并支持确定性 replay。

compiler 只读取通过校验的 sealed trace，再生成 Generated EPG。Agent 不直接输出完整事件图。

## Agent Definition

当前 Agent Definition 工作位于：

```text
projects/h2epr/agents/
```

当前已接受的 Agent Definition 包含：

- `knickerbocker-trust.md`
- `new-york-clearing-house.md`
- `national-bank-of-commerce.md`
- `j-pierpont-morgan.md`
- `trust-company-of-america.md`
- `lincoln-trust-company.md`
- `trust-company-presidents-committee.md`
- `source-register.md`
- `evidence-ledger.md`
- `decision-situations.md`

各文件分工如下：

| 文件 | 负责的内容 |
|---|---|
| Agent Definition | 角色、可用信息、权限、决策机制、intent、假设和限制 |
| source register | 采用来源、公开地址、文件哈希、采用范围和限制 |
| evidence ledger | claim、时间边界、参与者可得性、材料用途和撤回后果 |
| decision situations | 两角色共享的研究局面和可证伪扰动 |
| runtime/reducer | 实际状态、裁决和结果 |

当前 Knickerbocker Definition 包含四个 Decision Commitment，NYCH 包含五个。两份定义使用同一
十模块结构，但分别表达公司级流动性与求援决策、成员制清算机构的程序与资源边界。它们是已经接受的
`0.2.1` 参考 Definition，仍属于结果已暴露的探索性建模，不声称历史校准或独立验证。

Knickerbocker 与 NYCH 的 `0.2.1` Definition 已有接受的 V1 mapping 和可执行的非 Ray
conformance 切片。其他五份 Agent Definition 与五份 population model 已进入 Roster Definition
release v0.1，并由已接受的全 Roster consolidated mapping 与 bounded mapping-loader/conformance
profile 覆盖；它们仍未获得 participant policy 或全事件 executable binding。旧的三 tick 路径已经作为
`0.1.0-dev` 冻结工程夹具移入
`tests/fixtures/agents/panic_1907/minimal_binding_v0_1/`，只覆盖：

1. Knickerbocker 发出 support request；
2. NYCH 根据 member-facility 资格和程序权限作出 typed decline；
3. Knickerbocker 在收到结果后更新 operational posture。

该夹具用于验证旧 Definition binding、缺失信息处理、请求生命周期、权限、结果反馈和 replay，不能
作为当前 `0.2.1` Definition 的实现或 conformance 证据。

## 与 MASim 的关系

MASim 是 H2EPR 的基础参考，也是部分通用运行能力的来源。

### 直接借鉴

- simulator/runner 的生命周期；
- Markdown 定义与 Python 实现分离；
- kebab-case Definition 与 snake_case Python 模块的命名方式；
- Skill 驱动的设计检查；
- scenario 实现与 config 分开；
- deterministic trace、transport、reducer 和 seal。

### 需要重新设计

- H2EPR Agent Definition 保留事件身份，不要求首轮跨场景复用；
- 制度行动使用 request、review、authorize、decline 等语义，而不是统一映射为 buy/sell/hold；
- Agent 输出 intent，实际 result 由环境生成；
- evidence ledger 与 participant-available time 是 H2EPR 自己的研究资产；
- Rule 和未来 LLM 共享外部行为边界，但内部决策方法可以不同。

### 暂缓引入

- 公共 Agent archetype library；
- 固定的 Rule/LLM/RuleLLM/RAG 四变体矩阵；
- runtime RAG 和 provider；
- LLM-based evaluation；
- UI 和插件化场景系统。

MASim 保持独立，不引用 H2EPR。H2EPR 通过项目侧适配层使用所需能力。目前旧 G3、G4 compiler
adapter 和冻结 Agent 工程基线仍分别存在直接 MASim imports；在正式接入新的 Agent runtime 前，
需要将这些依赖整理为清楚的适配边界。

## 当前状态

| 部分 | 状态 |
|---|---|
| Contracts V1 | 已稳定，支持离线 schema 和跨对象校验 |
| Construction | G1 工程基线完成 |
| ParticipantArtifact / EventBundle | G2 工程基线完成 |
| Rule runtime / trace | G3 deterministic canary 完成 |
| Generated EPG compiler | G4 deterministic compiler 完成 |
| Agent Definitions | 七份 Definition 已接受；两角色构成可执行参考试验，全部产品由全 Roster consolidated mapping 覆盖 |
| Population models | 五份 `0.1.0` 群体模型已接受；组成、profile/posture 和响应参数保留为暴露的敏感性设定 |
| Roster Definition release | v0.1 已完成，固定 Roster v0.4、七份 Agent Definition、五份 population model、证据和接口哈希 |
| Definition implementation mapping | 两角色 V1 mapping 与非 Ray conformance 切片已完成；全 Roster consolidated mapping、carrier review 与 mapping-loader/conformance 已完成 |
| V1 carrier fit | 当前语义可通过内部映射和跨对象校验承载 |
| Event Scenario Definition | v0.1 已接受，闭合 12 个产品、115 个 observation placements、107 个 intent placements、13 类生命周期和 34 项跨对象规则 |
| Scenario Configuration | v0.1 已接受为非可执行机制覆盖配置，固定 16 actor、10 population capability units、9 个外生输入、8 个结构选择和 8 个敏感性 overlays |
| Configuration admission | v0.1 静态准入已通过，固定 raw/canonical identity、项目本地 schema、稳定错误分类、fail-closed loader、跨对象检查和 deterministic receipt；仍不可执行 |
| Historical evaluation | 延后到独立的 post-seal 工作 |

G1–G4 证明了工程链路可以运行。当前研究仍需继续验证 Agent 和 scenario 的科学合理性。GAP-01
保留了 NYCH 其他支援路径权限的不确定性；GAP-02 保留了 Knickerbocker 精确请求人和公司授权的
不确定性。

## 接下来的工作

### 当前迭代

H2EPR-0288 的 [Roster v0.4](h2epr/agents/rosters/panic_1907.md)、
[event semantic skeleton](h2epr/scenarios/panic_1907/semantic-skeleton.md) 和
[Roster Definition release v0.1](h2epr/releases/panic_1907/roster-definition-v0.1/) 已建立；
[consolidated mapping](h2epr/agents/bindings/panic_1907/consolidated/) 与
[Event Scenario Definition v0.1](h2epr/scenarios/panic_1907/definition-v0.1/) 已接受；
[Scenario Configuration v0.1](h2epr/configs/panic_1907/scenario-configuration-v0.1/)
也已作为非可执行机制覆盖配置正式提升；其
[bounded configuration admission v0.1](h2epr/configs/panic_1907/configuration-admission-v0.1/)
已完成 schema/canonical identity、稳定错误分类、fail-closed loader 和静态 receipt；独立的
[KT–NBC–NYCH bounded binding v0.1](h2epr/agents/bindings/panic_1907/kt-nbc-nych-v0.1/)
也已完成精确 carrier projection 与最小 policy/environment binding；其
[E7 conformance closeout](h2epr/scenarios/panic_1907/lineage-conformance-v0.1/)
完成 negative conformance、确定性 trace/replay、review 与方法 closeout。按照
[事件建模工作流](h2epr/WORKFLOW.md)，S0--S4 已完成并停止，不扩展到全 roster 或启动全事件模拟。

### 后续方向

完整 16-actor runtime、九项 policy 的全部实现、全事件 simulation、参数校准或历史拟合、
held-out/clean-builder 实验、post-seal 科学评价以及历史或科学有效性声明均不属于当前 S0--S4。
Rule v2、正式 simulation、post-seal evaluation、LLM/RAG 和多事件扩展仍需要各自的研究问题和
进入条件；下一步优先用第二事件检验方法复用性。

## 目录演进

只在出现实际消费者时增加新目录：

| 新目录或职责 | 建议触发条件 |
|---|---|
| 独立 `scenarios/` | 第二个微局面出现，或环境逻辑需要独立复用和测试 |
| theory prototype | 多个 Agent Definition 确实重复同一行为机制 |
| 第二事件目录 | 新事件已有明确问题、证据边界和角色范围 |
| evaluation package | post-seal 评价方法和数据边界已经确定 |
| 根级 H2EPR package | 出现仓库外使用者、独立发布或复现需求 |

旧三步实现保存在 `tests/support/agents/panic_1907_baseline.py`，只供冻结工程夹具使用。当前 Definition
不会复用该模块名称或映射；后续实现按 Agent、scenario/environment 和 reducer 的真实职责建立。

## 开发与版本管理

正式仓库保存当前版本：

- Agent Definition 使用 lowercase kebab-case；
- Python 模块使用 lowercase snake_case；
- 事件目录沿用 `panic_1907` 这类稳定标识；
- 简单 Skill 直接放在 `skills/*.md`；
- 不在正式目录保存 `-old`、日期后缀或临时副本。

更丰富的草稿、对比和研究过程保存在：

```text
.local-runtime/h2epr-simulation/working/
```

接受后的版本通过 Git history 保留。已经归档的来源、研究证据和正式运行记录继续保持原始内容。

## 测试

配置静态准入、Agent binding/conformance 和 V1 合同测试不启动 Ray：

```bash
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH=projects/h2epr/src \
python -B -m pytest -p no:cacheprovider \
  projects/h2epr/tests/configuration \
  projects/h2epr/tests/agents \
  projects/h2epr/tests/contracts
```

独立的
[H2EPR event-standardization CI](../.github/workflows/h2epr-event-standardization.yml)
自动运行 configuration admission、KT--NBC--NYCH Agent binding 和 E7 conformance
三个边界测试面。该 workflow 不启动 simulator，也不把 bounded E7 并入旧 G3/G4 运行路径。

其他测试入口和环境要求见 [tests/README.md](h2epr/tests/README.md)。

## 添加新内容时

提交新 Agent、字段或目录前，建议确认：

1. 它解决了哪个具体问题；
2. 哪个模块负责维护它；
3. 哪段代码、测试或人工审查会使用它；
4. 它属于通用 H2EPR 能力还是某个事件；
5. 是否重复了 evidence、scenario、contract 或 reducer 中已有的信息；
6. 什么结果会说明这项设计需要修改。

这些问题有助于保持项目结构简单，也让模板和 Skill 从实际使用中逐步成长。
