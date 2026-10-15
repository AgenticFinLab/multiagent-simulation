# 02 · 讨论决策记录（Decision Log）

> 记录已达成共识的决定，便于后续设计直接引用，不再反复讨论。

## D1：协议边界（讨论点 4）—— 已定

**决定：内部通信不走 A2A/MCP，只有“跨语言 / 跨系统 / 外部 / 工具”才走标准协议。**

- 内部（同进程/同集群的高频 agent 间消息）：用轻量内部消息总线（MASim 三层消息模型扩展），不引入协议开销。
- 外部：A2A（agent↔agent 跨语言/跨服务）、MCP（agent↔工具/知识/数据）、AG-UI（人机）。
- 理由：性能敏感路径不走协议；跨系统互操作才需要标准协议。

## D2：复合 agent 的嵌套与聚合（讨论点 5）—— 已定

**决定：把“嵌套”与“聚合”都做成接口，保持最大灵活性。**

1. **嵌套深度不设硬上限**：通过 `AgentRuntime.children()` 递归支持任意层级；仅用配置做软约束（如最大深度/最大子 agent 数），防止误配导致的失控。
2. **聚合（aggregation）留接口，不预先写死实现**：
   - 先定义聚合契约：`aggregate(child_results) -> summary`，接口含输入/输出 schema 与“统计量 + 离群样本 + 溯源引用”。
   - 提供 1~2 个默认实现（如简单统计聚合、LLM 摘要聚合），**按需再实现更复杂聚合**（层级、语义、多模态等）。
3. 好处：先能跑，再按场景逐步增强聚合，避免一开始过度设计。

## 待继续讨论（尚未定）

- 时间语义的两个子问题（见 `01-time-semantics-deep-dive.md` §5）：意图陈旧容忍度、刷新节奏/deadline。
- I1 的规模配比具体数值（活跃子集/抽样比例）——待后续规模实验标定。
- I10 的价值位定位是否正式采纳为项目定位。
- 是否还有需要纳入对照的已有工作（讨论点 6，持续补充）。

## 决策记录原则

- 每条决定带“理由 + 影响面”，后续设计文档用 `D1/D2/...` 引用。
- 一旦进入设计/实现，决定默认冻结；若需推翻，在此追加“变更记录”。

---

## 追加决定（第二轮讨论）

### D3：平台领域无关（讨论点 1，最终版）—— 已定
**决定：平台 = 领域无关的通用“多智能体模拟基础设施”；平台内没有任何领域层。金融/社会等由使用者自行实现。**
- 平台只提供通用原语与机制：agent 抽象、激活控制器、逻辑时间、拓扑、通信、状态、规模、协议、可观测。
- 不做市场/订单簿/金融指标等任何领域语义——那些是使用者用平台原语实现的“场景/示例”，不进平台。
- 价值位（I10 最终表述）：「领域无关的通用多智能体模拟基础设施 + 标准协议互操作 + 几十到几十万的异构规模降级」；金融是第一个参考示例。
- 详见 `03-platform-scope-and-domain-layer.md`。

### D4：逻辑时间（讨论点 3）—— 已定
**决定：时间语义采用“逻辑时间（round/level）+ 同步屏障 + 低频决策/高频执行 + 截止降级”，不模拟真实墙钟时间。**
- 详见 `05-logical-time-explained.md`（概念）与 `01-time-semantics-deep-dive.md`（展开）。

### D5：激活控制器（讨论点 2，更新版）—— 已定
**决定：激活是平台的一等基础设施模块（ActivationController），向被激活 agent 下发 ActivationSignal；策略可插拔。**
- 每个 agent 注册一个 ActivationPolicy（周期/事件/阈值/随机，可组合），组可绑活跃度曲线，控制器统一判定 + 分层抽样。
- 与 DecisionEngine 边界：激活控制器决定“谁动、给多少预算”，决策引擎决定“怎么决策”。
- 详见 `04-heterogeneous-activation.md`。

### 仍待你拍板
- D4 的两个子问题：意图陈旧容忍度（staleness 上界）、意图刷新节奏/默认 deadline。
- D5 的内置 policy 先给哪几类、分布跟随的噪声大小。
- 复合 agent（`06`）的三个待确认：先实现哪些组织模式、聚合默认实现、远端子 agent 是否先留接口。

### D4 补充：时间由专门模块负责 —— 已定
**Scheduler（逻辑时钟）是平台的一等模块（M2）**：维护 round/level/step + 同步策略接口（默认 strict）；与 ActivationController（M3，谁动）分工。
- 详见 `08-async-prefetch-explained.md` 与 `07-platform-modules.md`。

### D5 补充：激活控制器 —— 已确认
用户确认“激活 = 平台机制/模块”的方向；字段、触发器、集中判定三问待确认（见 `04` §8）。


### D4 再修正（关键澄清）—— 已定
- **撤回“投机预取 / 预测第 t 轮状态”的错误说法**：agent 没有观察就不能决策。
- 正确语义 = **低频决策（决策时有真实观察）+ 高频执行（规则用意图）+ 异步刷新（旧意图容忍陈旧）**。
- 详见 `08-async-prefetch-explained.md`（修正版）。


### D6：时钟/信号/同步策略（最终原则）—— 已定
**决定：平台只定义「时钟（Clock）+ 信号（Signal）+ 同步策略接口（SynchronizationPolicy）」；等待/异步/陈旧容忍均为使用者策略，平台默认只给 strict（严格等待）。**
- 平台不替使用者决定“某个 agent 要不要异步、超时怎么办、旧意图能不能用”。
- 详见 `09-clock-signal-and-sync.md`。

### D7：时间/激活域拆分 + 最小改造 —— 已定
**决定：时钟、同步策略、激活、信号拆成独立模块（M2 Clock / M3 Scheduler / M4 SynchronizationPolicy / M5 ActivationController / M6 Signal）；不放在同一模块。**
- 采用最小改造：能吸收进现有模块的扩展/重构现有（Clock 扩展 `ExecutionClock`、Scheduler 重构 `run_round`、SyncPolicy 替换 `ray.get`、Activation 挂在 `phase_execute`），不全面重写。
- 四阶段、Topology、Persona/Player、三层消息、Storage/断点续跑均不动。
- 详见 `11-module-refactor-mapping.md`。

### D8：三个小项落地方式 —— 已定（采用推荐默认）
1. **Signal 放 `masim/activation/signal.py`**（与激活同域，独立小文件）。
2. **ActivationController 做成顶层目录 `masim/activation/`**（含 controller + policy + signal）。
3. **SynchronizationPolicy 默认只实现 `strict` + 留接口**；`deadline` / `nonblocking` 后续按需补。

> 至此，讨论阶段的关键决策 D1–D8 全部冻结；进入「总体架构整合」阶段。

### D9：契约约定与契约包位置 —— 已定
- 制定《框架实现规定》：每个模块 `base.py` 只定义不实现（ABC + dataclass + 类型标注 + 文档），实现继承 base 增强。
- 契约包位于 `masim/platform/`，首批 11 个模块 base.py：agent / decision / composite / activation / runtime / message / state / topology / world / registry / scale。
- 详见 `docs/hybrid-design/FRAMEWORK-IMPLEMENTATION-RULE.md`。

### D10：4–6 号问题按推荐定案 —— 已定
**④ 协议边界：**
- ProtocolBridge 不写 base.py（是复用 MAF 的薄适配层，非平台自建）。
- MessageBus 第一版只做最简 Info→Message→SimPacket + RoutePolicy 接口；聚合消息/兴趣路由后续补。
- A2A 鉴权在桥契约中显式强制：AgentCard 只做发现，授权必须绑定鉴权。

**⑤ 复合深度与聚合：**
- 嵌套软约束默认 `max_depth=4 · max_children=32 · max_total_agents=1024`（可配置，后续实验标定）。
- 聚合默认实现先做两个：统计聚合 + LLM 摘要聚合。
- CompositeOrchestrator 第一版先做最简顺序编排 + Fan-out/Fan-in；MAF Workflow 后续接。

**⑥ 补充范围：**
- 补充「评估基准」与「多智能体辩论/MoA」两类，以“简述 + 可借鉴点”形式，写入 `examples/_platform-notes/`。

> 4–6 全部冻结；进入「深入文章总结 + 实现参考」补充阶段（不写代码）。
