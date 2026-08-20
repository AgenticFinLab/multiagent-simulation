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

当前工作重点已经转向 Agent Definition。第一轮使用 1907 年金融恐慌中的 Knickerbocker Trust
和 New York Clearing House（NYCH），检查两个制度角色能否通过同一套方法得到清晰、可执行的
行为定义。

## 文档导航

| 文档 | 内容 |
|---|---|
| 本页 | 仓库结构、模块关系和开发方向 |
| [Research projects](README.md) | `projects/` 目录中的研究项目索引 |
| [H2EPR README](h2epr/README.md) | 已有功能、运行边界和测试入口 |
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
├── contracts/v1/             # 稳定合同和 JSON Schema
├── decisions/                # 架构决策记录
├── configs/panic_1907/       # 1907 canary 配置
├── agents/
│   ├── agent-definition-template.md
│   └── defines/panic_1907/
├── skills/
│   ├── historical-evidence-research/
│   ├── participant-behavior-research/
│   ├── agent-definition/
│   └── agent-definition-review/
├── src/h2epr/
│   ├── construction/
│   ├── artifacts/
│   ├── policies/
│   ├── world/
│   ├── bundles/
│   ├── agents/
│   ├── runtime/
│   └── compiler/
└── tests/
```

### 模块职责

| 路径 | 用途 |
|---|---|
| `contracts/v1/` | Construction、runtime、trace、seal、Generated EPG 等机器接口 |
| `construction/` | 加载明确授权的来源，并生成 typed、lossless Construction IR |
| `artifacts/` | EntityRegistry、provenance 和 ParticipantArtifact |
| `policies/` | 现有 Rule canary 使用的声明式策略 |
| `world/` | canary 世界状态和纯计算函数 |
| `bundles/` | Construction bundle、EventBundle 及其校验 |
| `agents/` | 当前 Agent Definition 研究资产、通用 binding 约束和冻结工程基线 |
| `runtime/` | H2EPR 的 MASim 适配、Rule runtime、detector 和 runner |
| `compiler/` | 校验 sealed trace，并生成 EPG 和 GraphSeal |
| `tests/` | 合同、construction、runtime、compiler 和 Agent 测试 |

`skills/` 按证据研究、角色行为研究、Definition 编写和独立审核分层。每个
Skill 以 `SKILL.md` 作为入口，并把详细研究规范放在相邻 `references/` 中。

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

第一轮包含：

- `knickerbocker-trust.md`
- `new-york-clearing-house.md`
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
`0.2.0` 参考候选，仍属于结果已暴露的探索性建模，不声称历史校准或独立验证。

当前 `0.2.0` Definition 尚无可执行 binding。旧的三 tick 路径已经作为 `0.1.0-dev` 冻结工程夹具
移入 `tests/fixtures/agents/panic_1907/minimal_binding_v0_1/`，只覆盖：

1. Knickerbocker 发出 support request；
2. NYCH 根据 member-facility 资格和程序权限作出 typed decline；
3. Knickerbocker 在收到结果后更新 operational posture。

该夹具用于验证旧 Definition binding、缺失信息处理、请求生命周期、权限、结果反馈和 replay，不能
作为当前 `0.2.0` Definition 的实现或 conformance 证据。

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
| Agent Definition 0.2.0 | 两角色参考 Definition、来源表、claim ledger 和决策局面已接受 |
| Definition implementation mapping | 尚未开始；旧三步路径仅作为冻结工程基线 |
| V1 carrier fit | 当前语义可通过内部映射和跨对象校验承载 |
| Historical evaluation | 延后到独立的 post-seal 工作 |

G1–G4 证明了工程链路可以运行。当前研究仍需继续验证 Agent 和 scenario 的科学合理性。GAP-01
保留了 NYCH 其他支援路径权限的不确定性；GAP-02 保留了 Knickerbocker 精确请求人和公司授权的
不确定性。

## 接下来的工作

### 当前迭代

下一轮使用 Knickerbocker 和 NYCH 完成 Definition-to-implementation mapping：

- 映射 Definition identity、Decision Commitment、observation 和状态；
- 映射 intent、权限、business result 与 trace 记录；
- 明确保留哪些 backend 自由度，哪些属于硬 conformance 边界；
- 通过角色互换、信息遮蔽、请求生命周期和无效 intent 检查映射。

### 映射完成后

根据两角色映射和反馈结果，再决定是否需要修订 Definition、Template 或 Skills，并判断是否已经具备
进入实现迭代的条件。

如果实际映射出现 V1 无法表达的案例，再评估窄范围的 successor contract。目录或字段风格本身不构成
修改合同的理由。

### 后续方向

Rule v2、正式 simulation、post-seal evaluation、LLM/RAG 和多事件扩展都需要各自的研究问题和
进入条件。项目会根据前一轮结果决定下一步，而不是预先固定完整阶段表。

## 目录演进

只在出现实际消费者时增加新目录：

| 新目录或职责 | 建议触发条件 |
|---|---|
| 独立 `scenarios/` | 第二个微局面出现，或环境逻辑需要独立复用和测试 |
| theory prototype | 多个 Agent Definition 确实重复同一行为机制 |
| 第二事件目录 | 新事件已有明确问题、证据边界和角色范围 |
| evaluation package | post-seal 评价方法和数据边界已经确定 |
| 根级 H2EPR package | 出现仓库外使用者、独立发布或复现需求 |

旧三步实现保存在 `src/h2epr/agents/panic_1907_baseline.py`，只供冻结工程夹具使用。当前 Definition
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

冻结 Agent 工程基线和 V1 合同测试不启动 Ray：

```bash
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH=projects/h2epr/src \
python -B -m pytest -p no:cacheprovider \
  projects/h2epr/tests/agents \
  projects/h2epr/tests/contracts
```

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
