# 框架契约 · Player 生命周期与线格式（Framework Contract）

> **本文是 Player 生命周期的权威契约**：`docs/structure.md` §2、`docs/llm-coding-rules.md` §11、
> `masim/player/general.py` 的 `on_fill` 文档、以及 `scripts/audit_scenario_contract.py` 的检查项都引用本文件。
>
> 适用范围：所有金融场景的 `players.py`（`examples/{Scenario}/{Rule,LLM,RuleLLM,Rag}/`）与所有可复用
> archetype（`masim/agents/{finance,market,opinion}/`）。
>
> 术语：**契约（contract）**= 框架保证；**扩展点（hook）**= 子类被允许覆盖的方法。

---

## 1. 契约范围与生效方式

框架在 `decide()` 与 `act()` 之间提供三项保证，只有在**不覆盖框架方法**时才成立：

1. **线格式键完整**：`action` / `quantity` / `bid_price` 必须存在且可转为期望类型；
2. **非 HOLD 单必须正价**：`bid_price > 0`，由 `require_positive_bid_price()`（`masim/format/finalize.py:68`）强制，**不允许**静默回退到 `market_data["price"]`；
3. **现金与仓位恰好变更一次**：由框架统一执行，见 §6。

此外，每个 agent 使用**自己的**随机流（§7），并只在 `on_fill` 中做逐笔状态维护（§4）。

---

## 2. 基类与继承关系

四个 canonical 基类都直接派生自 `GeneralPlayer`（`masim/player/general.py`），并混入 `SeededRngMixin`：

| 基类 | 文件 | 用途 |
|------|------|------|
| `CanonicalRulePlayer` | `masim/agents/_base.py:430` | 确定性公式型 investor |
| `CanonicalLLMPlayer` | `masim/agents/_base.py:621` | LLM 决策型 investor |
| `CanonicalRagPlayer` | `masim/agents/_rag_base.py:64` | `CanonicalLLMPlayer` + 检索上下文 |
| `CanonicalMarketCoordinator` | `masim/agents/_coordinator_base.py:57` | 市场/价格形成协调者（始终规则执行） |

`SeededRngMixin`（`masim/agents/_base.py:406`）只提供 `rng` 属性（`:416`），不定义 `__init__`、
不覆盖任何 Player 方法，因此 MRO 为 `Class → SeededRngMixin → GeneralPlayer → BasePlayer → ABC`。

> **方向反转**：investor 消费广播、产出订单；coordinator 消费订单、产出广播
> （`masim/agents/_coordinator_base.py:6-7`）。

---

## 3. 生命周期：`perceive → decide → act`

每轮每 agent 调用一次 `PlayerPersona.operate()` → `Player.turn()` → `step()`，其中：

```
perceive(observation)   # 框架实现；把市场广播写入 custom_state
      ↓
decide()                # 框架实现；调用子类扩展点产出 InvestorOrder/线格式 dict
      ↓
act(payload)            # 框架实现；校验 → 更新现金/仓位 → on_fill() → Action
```

框架实现位置：

| 基类 | perceive | decide | act |
|------|----------|--------|-----|
| Rule | `_base.py:461` | `_base.py:482` | `_base.py:512` |
| LLM | `_base.py:658` | `_base.py:678` | `_base.py:720` |
| Coordinator | `_coordinator_base.py:84` | `_coordinator_base.py:103` | `_coordinator_base.py:122` |

**`perceive` 的职责**：记录 `round`、惰性初始化状态（`cash`/`position`/`rng`/`price_history`，见
`_base.py:555`）、把带 `price` 的入向广播写入 `custom_state["market_data"]`、向
`price_history` 追加价格，并回调 `on_market_data()`。

**`decide` 的职责**：Rule 由 `StandardMarketState` → `decide_order()` → `_finalize_order()` →
`_emit()`；LLM 由 prompt → 模型 → 场景 schema 校验 → `_finalize_llm_order()` → `_emit()`。
LLM 调用失败**向上抛出**，不伪造 hold（`_base.py:689-701`）。

**`act` 的职责**：委托给 `_apply_fill_and_emit_action()`（`_base.py:332`），Rule 与 LLM 共用同一实现，
因此两条路径在线格式与现金语义上**不可能漂移**。

---

## 4. `on_fill` 契约（逐笔状态维护的唯一入口）

```python
def on_fill(self, action: str, quantity: float, bid_price: float) -> None:
    """成交后钩子，默认 no-op。"""
```

`on_fill` 由 `_apply_fill_and_emit_action()` 在**校验之后、现金/仓位变更之后**调用恰好一次
（`masim/agents/_base.py:395-397`）。

契约要点：

1. **入参已校验**：`action ∈ {buy, sell, hold}`；当 `action ∈ {buy, sell}` 且 `quantity > 0` 时
   `bid_price > 0` 必然成立。因此**不可能**出现“按 0 价静默成交”的记账。
2. **默认实现为空**（`masim/player/general.py:136`）：不需要逐笔状态的 archetype 不必实现。
3. **仅用于逐笔状态**：VWAP 锚、成本基础、持仓均价、累计成交笔数、处置效应阈值等。
4. **调用次数**：每个通过校验的 BUY/SELL 各一次；HOLD 也会触发（`bid_price` 为原始值），
   需要过滤时由实现自行判断。
5. **不要在 `on_fill` 里改 `cash` / `position`**：框架已经改过，重复修改会造成双重计数。

追踪来源：用户上下文中的 `AGENT_POOL` 档案要求“逐笔状态更新走 `on_fill`”即指本节。

---

## 5. 允许的扩展点（按引擎）

**覆盖以下方法 = 违约**（由 §8 的审计脚本报告 `STRUCT-ACT` / `STRUCT-DECIDE` / `STRUCT-PERCEIVE`）：

```
perceive()   decide()   act()
```

框架方法（`decide`/`act`）拥有线格式校验与记账；覆盖它们会绕过 §1 的三项保证。

被允许的扩展点：

| 基类 | 扩展点 | 位置 | 用途 |
|------|--------|------|------|
| Rule | `decide_order(state) -> InvestorOrder \| dict` | `_base.py:523` | **必需**：策略本体 |
| Rule | `init_extras(extras)` | `_base.py:536` | 读取 archetype 参数（一次性） |
| Rule | `on_market_data(market_data)` | `_base.py:545` | 每次广播到达时的滚动窗口维护 |
| Rule/LLM | `on_fill(action, quantity, bid_price)` | `_base.py:395` 调用 | 逐笔状态（§4） |
| LLM | prompt 类常量 + `_format_user_prompt()` | `_base.py` | 提示词与 schema 选择 |
| RAG | `_build_rag_query(state)` | `_rag_base.py:96` | 检索查询构造 |
| Coordinator | `init_market_state(extras)` | `_coordinator_base.py:133` | 市场状态初始化 |
| Coordinator | `advance_market(...)` | `_coordinator_base.py:143` | 价格/状态推进 |

类级元数据（供定制化 UI 与审计使用）：`STRATEGY`、`DISPLAY_NAME`、`SUMMARY`、`REQUIRES_FEATURES`、
`PARAM_SPECS`。

> `PARAM_SPECS` 用于 `validate_archetype_extras()`（`_base.py`）在 actor 创建**之前**做参数预检。
> 目前只有 10/209 个 archetype 声明了它，因此绝大多数 archetype 的 `extras` 没有类型/范围校验
> —— 这是已知待补项（见 `docs/structure.md`）。

---

## 6. 线格式与唯一收敛点

**订单对象**：`InvestorOrder`（`masim/format/order.py:104`，frozen dataclass）字段
`action / quantity / bid_price / investor / strategy`，另带溯源字段
`skipped / skipped_reason / clipped / clipped_from / clipped_intended_quantity / clipped_reason`，
使「被裁剪的 BUY/SELL 变成 hold」可与「显式 hold」在指标层区分。

**唯一收敛点**：`masim/format/finalize.py`

| 函数 | 作用 |
|------|------|
| `require_positive_bid_price()` `:68` | 非 HOLD 单正价强校验（fail-loud） |
| `clip_order_to_liquidity()` `:148` | 按现金/持仓裁剪数量 |
| `finalize_rule_order()` `:226` | Rule 路径终结器（`bid_price ≤ 0` 时用 `state.price` 补齐，沿用历史语义） |
| `finalize_llm_order()` `:290` | LLM 路径终结器（分类感知；仅 `participation_order` 允许显式替换） |
| `emit_order_envelope()` `:352` | 生成线格式 dict（含 `outbound_messages` 信封） |

`_apply_fill_and_emit_action()`（`_base.py:332`）在 `act()` 中做**纵深防御**：再次调用
`require_positive_bid_price()`、更新 `cash`/`position`、触发 `on_fill`、构造 `Action`。

**禁止**：在场景代码中复刻“非正价就取 `market_data["price"]`”的静默回退
（`docs/llm-coding-rules.md` §11.5 有正则级禁令）。

---

## 7. 随机性与可复现

- 运行级种子：`setting.seed`（YAML）。为 `null` 时不可复现（各 agent 仍是独立流）。
- 框架把它注入每个 player 的 `extras["seed"]`（`masim/simulator/general.py`），再由
  `derive_rng(seed, salt=identity)`（`masim/utils/rng.py`）派生**按 agent 加盐**的
  `random.Random`，存于 `custom_state["rng"]`。
- archetype **必须**通过 `self.rng`（`SeededRngMixin`）取随机数，**禁止**使用全局 `random` 模块：
  全局流在 Ray worker 之间共享且不可复现。唯一例外是 `masim/agents/_base.py` 中 LLM API key 轮换的
  `random.choice`（不应消耗仿真随机流）。
- `run_manifest.json` 记录 seed、轮数、git commit 与 player 类清单，随产物落盘。

---

## 8. 强制与审计

**断言脚本**：`scripts/audit_scenario_contract.py`

| 检查 | 含义 | 严重度 |
|------|------|--------|
| `STRUCT-ACT` | canonical 子类覆盖 `act()` | CRITICAL |
| `STRUCT-DECIDE` | canonical 子类覆盖 `decide()` | CRITICAL |
| `STRUCT-PERCEIVE` | canonical 子类覆盖 `perceive()` | CRITICAL |
| `SEM-SILENT-FILL` | 静默回退 `bid_price`（排除文档字符串与算术变换） | HIGH |
| `SEM-CASH-MUT` | 在 `init/on_fill` 之外直接改 `cash` | HIGH/MEDIUM |
| `LEGACY-BASE` | 直接继承 `GeneralPlayer` | INFO |

扫描范围：`--scope scenarios`（`examples/*/{Rule,LLM,RuleLLM,Rag}/players.py`）、`--scope archetypes`
（`masim/agents/{finance,market,opinion}/*.py`）或 `--scope all`（默认）。

**CI 门禁**（`.github/workflows/contract-audit.yml`）：

1. 参考场景 `AnchoringEffect` —— **必须 CLEAN**；
2. archetype 库 —— **必须 CLEAN**（当前为 0 findings）；
3. 其余场景语料 —— 仅基线，不阻断（迁移未完成）。

**注意**：`STRUCT-*` 只对 canonical 子类生效。当前 180 个 `players.py` 中：**1** 个在文件内声明
canonical 类（`examples/AnchoringEffect/Rag/players.py`）；**4** 个是合规的**组合式**薄模块
（从 `masim/agents/` 重导出 archetype，`AnchoringEffect/{Rule,LLM,RuleLLM}`、`TulipMania/Rule`）；
**175** 个仍直接继承 `GeneralPlayer`（`LEGACY-BASE`）。因此在迁移完成前，`STRUCT-*` 的 0 findings
对 **175 个 legacy 文件不构成证明** —— 审计脚本会打印这份迁移进度表。

---

## 9. 迁移现状与步骤

**现状**：209 个 archetype 已全部遵循本契约（0 个覆盖 `act`/`decide`/`perceive`，
200 个实现 `decide_order`，5 个实现 `on_fill`）；场景层仅 `AnchoringEffect` 完成迁移。

**把一个场景迁移到 canonical 基类**：

1. 把 `players.py` 中的 investor 类基类从 `GeneralPlayer` 改为 `CanonicalRulePlayer`
   （或按机制改为 `CanonicalLLMPlayer` / `CanonicalRagPlayer`），把策略从 `decide()` 搬进
   `decide_order(state) -> InvestorOrder`，删除自实现的 `act()`（现金/仓位/校验由框架负责）。
2. 协调者类改为 `CanonicalMarketCoordinator`，策略搬进 `advance_market()`。
3. 逐笔状态维护搬进 `on_fill()`（§4）；每次广播的窗口维护搬进 `on_market_data()`。
4. 参数从 `self.config.extras` 读取（`init_extras`），并补齐 `PARAM_SPECS` 以获得预检。
5. 在 `configs/{Scenario}/{Mech}/simulation.yml` 设置 `setting.seed`。
6. 运行 `python scripts/audit_scenario_contract.py --scope scenarios --scenario {Scenario}` 直到 CLEAN。

---

## 10. 相关文件

| 内容 | 位置 |
|------|------|
| 框架基类实现 | `masim/agents/_base.py` · `_coordinator_base.py` · `_rag_base.py` |
| Player 基类与 `on_fill` 默认实现 | `masim/player/general.py` · `masim/player/base.py` |
| 线格式与终结器 | `masim/format/order.py` · `masim/format/finalize.py` |
| 市场状态契约 | `masim/format/state.py` |
| 随机性 | `masim/utils/rng.py` |
| 断言脚本 | `scripts/audit_scenario_contract.py` |
| 代码规范（§11 契约条款） | `docs/llm-coding-rules.md` |
| 结构与模块总览 | `docs/structure.md` |
