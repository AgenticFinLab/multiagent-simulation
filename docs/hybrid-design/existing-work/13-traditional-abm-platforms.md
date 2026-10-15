# 13 · 传统 ABM 平台与 GPU 仿真（补充）

> 传统 ABM 平台不接 LLM，但它们是“几十万~百万 agent 仿真”的**性能与建模经验**源头。

## 1. 平台谱系（按抽象层级）

| 平台 | 语言 | 规模/性能 | 特点 |
|------|------|-----------|------|
| NetLogo | Logo | 单机，易用 | 最高层抽象，教学/原型首选 |
| Mesa | Python | 单机 | 我们已选用的 Python ABM 思想来源 |
| MASON | Java | 单机，快 | 追求速度，学术界常用 |
| Repast | Java/C++ | 单机/HPC | Swarm 系，HPC 扩展 |
| GAMA | GAML | 单机/GIS | 空间 + GIS 强 |
| AnyLogic | Java | 企业级 | 商业，多方法（ABM/SD/DE） |
| Agents.jl | Julia | 单机/多线程 | 现代、高性能、易用 |
| FLAME GPU / flame | C/CUDA | **GPU 百万级** | agent 函数编译为 CUDA kernel，单卡百万 agent 实时 |

## 2. FLAME GPU（最重要的规模化参考）

- 核心：**把 agent 函数编译为 CUDA kernel**，agent 状态驻留 GPU 显存，消息在 GPU 内传递。
- 效果：一块工作站级 GPU 可**实时模拟百万级 agent**；随 agent 数增加，GPU 优势越明显。
- 适用：**规则/数值型 agent**（不含 LLM），非常适合“市场微观结构 + 大量规则交易者”。

### 启示
- 我们的 L3（几十万）里，**绝大多数 agent 是规则/数值型**，这部分其实可以参考“GPU 批量规则引擎”的思路。
- 但 GPU 与 LLM 异构，需分层：**规则洪流走 GPU/向量化，LLM 决策走 CPU worker 池**。

## 3. 传统 ABM 的建模资产（可保留的概念）

1. **Model / Scheduler / Space 分离**（Mesa）。
2. **时间步 + 离散事件混合**（Mesa experimental.devs、AnyLogic DE）。
3. **同步全体行动 + 冲突随机解决**（多数 ABM 的默认语义）。
4. **数据采集器 / 指标**（Mesa DataCollector）。
5. **可复现：同 seed 同结果**（所有正规 ABM 平台共识）。

## 4. 对我们的一条重要判断

> 传统 ABM 解决“百万规则 agent”，LLM 框架解决“少量智能 agent”，**中间缺的是“把两者放进同一个世界、同一个时钟、同一套市场”的混合运行时**。这正是本项目的价值位（呼应 I10）。

## 5. 与 GPU 路线的关系（边界）

- GPU 化规则 agent 是**可选加速项**，不是第一步必需。
- 第一步先用 Ray 把规则路径做对（可复现、可 checkpoint），GPU 作为 L3 的后期优化。
- 避免“为百万而 GPU，结果 LLM 路径没打通”的误区。
