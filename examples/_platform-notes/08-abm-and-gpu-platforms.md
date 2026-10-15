# 08 · 传统 ABM 平台与 GPU 仿真

> 核心问题：传统 ABM 给我们的“建模概念”与“百万规则 agent 性能”经验。

## 1. 平台谱系

| 平台 | 语言 | 规模/性能 | 特点 |
|------|------|-----------|------|
| NetLogo | Logo | 单机易用 | 教学/原型 |
| Mesa | Python | 单机 | Model/Scheduler/Space 分离 |
| MASON | Java | 单机快 | 学术界常用 |
| Repast | Java/C++ | 单机/HPC | Swarm 系 |
| GAMA | GAML | 单机/GIS | 空间+GIS 强 |
| AnyLogic | Java | 企业级 | ABM/SD/DE 混合 |
| Agents.jl | Julia | 多线程 | 现代高性能 |
| FLAME GPU / flame | C/CUDA | GPU 百万级 | agent 函数编译为 CUDA kernel |

## 2. FLAME GPU（最重要的规模化参考）

- 把 agent 函数编译为 CUDA kernel，agent 状态驻留 GPU 显存，消息在 GPU 内传递。
- 一块工作站 GPU 可实时模拟**百万级规则 agent**；agent 越多，GPU 优势越明显。
- 适用：规则/数值型 agent（不含 LLM）。

### 对实现的启示
- L3 里绝大多数 agent 是规则型，可参考“批量规则引擎/向量化”，但不是第一步。
- **规则洪流走 GPU/向量化，LLM 决策走 CPU worker 池**——不同执行路径不要混。

## 3. 传统 ABM 的建模资产（可保留的概念）

1. Model / Scheduler / Space 分离（Mesa）。
2. 时间步 + 离散事件混合（Mesa devs / AnyLogic DE）。
3. 同步全体行动 + 冲突随机解决。
4. DataCollector 采集指标。
5. 同 seed 同结果（可复现共识）。

## 4. 一条关键判断

传统 ABM 解决“百万规则 agent”，LLM 框架解决“少量智能 agent”，**中间缺一个把两者放进同一世界/时钟/市场的混合运行时**——这正是平台的价值位（呼应 I10/D3）。

## 5. 落到平台契约

- `Topology`（交互图/层级）对应 Model/Space。
- `Scheduler` + `Clock` + `SynchronizationPolicy` 对应 Scheduler（时间步 + 事件混合）。
- `DataCollector` 对应 DataCollector。
- GPU 规则引擎是 `DecisionEngine`（Rule）的后期优化，不进第一版。
