# 11 · 模块拆分与最小改造映射（时间与激活域）

> 结合你的意见：**这几个部分不放同一个模块；能吸收进现有模块的就别全面重写。**

## 1. 原则

1. **拆分**：时钟、同步策略、激活、信号，各自独立，不混在一个“Scheduler”里。
2. **最小改造**：优先扩展/重构现有模块，不推倒重写。
3. **保留现有接缝**：`phase_*`、`update_topology`、`persona/player/communication/proxy` 的既有边界不动。

![现状代码 → 平台契约 落库对照图](../diagrams/migration-mapping.png)

## 2. 拆分后的 5 个独立模块（时间与激活域）

| 模块 | 单一职责 | 吸收/改造现有 |
|------|----------|----------------|
| **Clock** | 逻辑时间 `round/level/step` + 耗时统计 | 扩展 `ExecutionClock` |
| **Scheduler** | 轮循环编排：把 clock + sync + activation + phase 串起来 | 重构 `BaseSimulator.run_round` |
| **SynchronizationPolicy** | 怎么等：strict / deadline / nonblocking | 新增接口，替换硬编码 `ray.get` |
| **ActivationController** | 谁动 + 预算 + 抽样 | 新增，挂在 `phase_execute` 前 |
| **Signal** | `ActivationSignal` / `Barrier` / `Deadline` | 新增 dataclass |

> 之前把“时钟+同步+预取+截止”都塞进一个 M2 Scheduler 是不对的，已按此拆分修正。

## 3. 现状 → 目标 映射（具体到现有代码）

| 目标模块 | 现有 MASim 位置 | 改动类型 | 改动量 |
|----------|-----------------|----------|--------|
| Clock | `masim/simulator/base.py::ExecutionClock` | 扩展：加 `round/level/step` 逻辑时间字段 | 小 |
| Scheduler | `masim/simulator/general.py::run_round` | 重构：改为委托 clock/sync/activation/phase | 中 |
| SynchronizationPolicy | 无（`phase_collect` 里硬编码 `ray.get`） | 新增接口 + `strict` 默认 | 小 |
| ActivationController | 无（`phase_execute` 对全 handle `operate`） | 新增 + `AllActive` 默认（行为不变） | 中 |
| Signal | 无 | 新增 dataclass | 小 |

## 4. 哪些完全不动（避免全面调整）

- 四阶段语义 `execute → collect → dispatch → record` 保留。
- `TopologyGraph.get_execution_levels()` 保留。
- `PlayerPersona.operate / receive_message`、`Player`、`on_fill` 契约保留。
- `Info → Message → SimPacket` 三层消息保留。
- `StorageProxy`、断点续跑 `detect_resume_round / write_resume_checkpoint` 保留。

## 5. 最小改造顺序（每步行为不变，可逐步落地）

1. **抽 `SynchronizationPolicy`**：接口 + `strict` 默认，替换 `phase_collect` 的 `ray.get`（风险最低）。
2. **扩展 `ExecutionClock` → `Clock`**：加入 `round/level/step`，保留耗时统计。
3. **新增 `Signal` dataclass**：定义 `ActivationSignal / Barrier / Deadline`。
4. **新增 `ActivationController` + `ActivationPolicy`**：默认 `AllActive`（每轮全激活，行为与现在一致）。
5. **重构 `run_round` → `Scheduler`**：把上述模块串起来（此时行为仍等价，只是结构更清晰）。

> 关键：**每一步单独提交/验证，行为保持等价**，最后才引入新的激活/同步策略。

## 6. 待你确认

1. `Signal` 放哪：独立 `masim/runtime/signal.py`、还是并进 `masim/activation/`、还是复用 `masim/communication`？（我建议放 `masim/runtime/` 或 `masim/activation/`，独立成小文件。）
2. `ActivationController` 是否做成顶层目录 `masim/activation/`？
3. 同步策略默认实现先只给 `strict`，`deadline`/`nonblocking` 后续按需？（结合 D6，我建议只给 strict + 留接口。）
