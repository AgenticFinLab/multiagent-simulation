# 10 · 现状对照：MASim 的“时间/同步/激活”现在是什么样

> 回答：这一部分是不是独立模块？当前框架有没有做好？设计是否合理、是否便于使用者调整？

## 1. 一句话结论

**现在“时间/同步/激活”不是独立模块，而是内联在 `GeneralSimulator.run_round()` 与 `phase_*()` 里；`ExecutionClock` 只是性能计时器，不是逻辑时钟/屏障调度器；“等待”硬编码在 `phase_collect` 的 `ray.get`；“激活”目前不存在（每轮所有 agent 都跑）。**

## 2. 现状逐项对照（代码位置 → 现状 → 是否可调）

| 目标能力（我们刚定的） | MASim 现状 | 所在位置 | 是否独立/可调 |
|------------------------|------------|----------|----------------|
| 逻辑时钟 Clock | 只有 `ExecutionClock`，**只统计耗时**，不管“谁等谁、怎么推进” | `masim/simulator/base.py` | 否（是计时器） |
| 轮次/层级推进 | `run_round` 里 `get_execution_levels()` → for level → 四阶段 | `masim/simulator/general.py` | 内联 |
| 同步策略 SyncPolicy | **硬编码严格等待**：`phase_collect` 直接 `ray.get(all futures)` | `general.py phase_collect` | 否（写死） |
| 激活 Activation | **不存在**：`phase_execute` 对每个 level 的所有 handle 都 `operate.remote()` | `general.py phase_execute` | 否（全跑） |
| 信号 Signal | 无显式信号类型；只有 `RoundPhase` 枚举（PENDING/EXECUTING/COMPLETE） | `base.py` | 否 |
| 阶段钩子 | `phase_execute / phase_collect / phase_dispatch` 是抽象方法，`update_topology` 是扩展钩子 | `base.py` | **是（好的种子）** |

## 3. 合理之处（要保留）

1. **四阶段分解很清晰**：`execute → collect → dispatch → record`，且 `phase_*` 是抽象方法——这是把“循环”拆成可替换步骤的正确方向。
2. **`update_topology(round)` 扩展钩子**：子类可动态改拓扑（配合 `invalidate_levels_cache`），这是“拓扑可插拔”的雏形。
3. **`ExecutionClock`**：把“耗时统计”和“轮次推进”分开统计，方向对，只是职责太窄（只管耗时，不管逻辑时间/屏障）。
4. **`is_received_ready` / `get_received_senders`**：agent 侧已有“就绪检查”的雏形，虽然目前默认恒真。

## 4. 不合理/不便之处（要改）

1. **“等待”写死**：`ray.get` 就是严格的同步屏障，使用者无法换成 deadline / nonblocking。
2. **“谁该跑”写死**：每轮所有 agent 都 `operate`，没有“激活控制器”，也就没有“活跃子集/抽样”。
3. **“时钟”与“耗时”混为一谈**：没有一个真正的“逻辑时钟 + 屏障 + 信号”模块。
4. **轮循环内联**：想调整“推进节奏”，使用者要改/继承 `run_round`，而不是配置一个策略。

## 5. 结论：需要抽成独立模块，但不必推倒重写

目标是把下面这些**从 `run_round` 里抽出来、变成独立可插拔模块**：

```text
Clock（逻辑时间 round/level/step）
SynchronizationPolicy（strict / deadline / nonblocking）  ← 替换硬编码 ray.get
ActivationController（谁跑 + 预算 + 抽样）                 ← 替换“全跑”
Signal（ActivationSignal / Barrier / Deadline）           ← 新增
```

好消息是：**现有 `phase_execute/collect/dispatch` + `update_topology` 钩子就是很好的接缝**，改造是“抽取 + 加接口”，不是重写。

## 6. 给使用者“可随意调整”的形态（目标）

```text
使用者只改配置/挂插件：
  - 想“严格等待”还是“到点降级” → 换 SynchronizationPolicy
  - 想“哪些 agent 这轮动”     → 挂 ActivationPolicy
  - 想“动态改谁跟谁交互”       → 用 update_topology 钩子
```

平台内核不变，行为由使用者拼装。

## 7. 下一步建议

先确认“抽取边界”，再进入实现：
1. 时钟是否拆成「逻辑时钟（round/level/step）+ 性能时钟（耗时）」两层？我建议拆。
2. `phase_collect` 的 `ray.get` 是否替换为一个 `SynchronizationPolicy` 接口？我建议替换。
3. 激活控制器是否独立成一个模块、挂在 `run_round` 与 `phase_execute` 之间？我建议独立。
