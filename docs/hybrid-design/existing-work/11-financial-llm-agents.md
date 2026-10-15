# 11 · 金融领域 LLM agent（补充）

> 上一轮已覆盖 TwinMarket / MarketSim / TradingAgents / EconAgent / CompeteAI。这里补充“单智能体/小团队”的金融 LLM agent，重点是**记忆、反思、市场智能**怎么做。

## 1. FinAgent（多模态金融基础 agent）

- 核心模块：**市场智能模块**（数值 + 文本 + 视觉多模态）、**双层反思**、**多样化记忆检索**。
- 目标：把多模态市场数据变成可执行交易决策。
- 启示：**“市场智能 + 双层层反思 + 记忆检索”** 是金融 agent 的“感知-反思-记忆”范本。

## 2. FinMem（分层记忆 + 角色设计）

- 三个模块：**Character（角色定制）· Memory（分层消息处理）· Decision-making（决策）**。
- 关键：**分层记忆**——把多源、多时间尺度的金融数据按层级吸收；自适应角色以应对市场波动。
- 启示：**金融记忆要分层**（高频行情 / 日度事件 / 长期风格），不能只一条扁平记忆流。

## 3. FinGPT（开源金融大模型）

- 核心：开源 FinLLM，RLSP（Reinforcement Learning from Stock Prices）把预测与市场结果对齐；LoRA 微调；实时数据管道（新闻/财报/社交）。
- 定位：金融 NLP 与信号抽取的“模型层”，不是完整 agent。
- 启示：金融专用小模型可做**信号抽取/情绪**，降低通用 LLM 的成本（属于“我们可选用”的模型层）。

## 4. QuantAgents（模拟交易多 agent）

- 四个 agent：模拟交易分析师、风控分析师、市场新闻分析师、经理，通过多轮会议协作。
- 定位：**在模拟交易里评估投资策略与市场场景，不冒真实风险**。
- 启示：**“分析师 + 风控 + 经理”的会议结构** = 复合 agent 内部 supervisor 的又一范本。

## 5. FinRobot（金融 AI agent 平台）

- 四层：Financial AI Agents 层（Financial CoT：收集数据→分析→规划→执行）、LLM 算法层、数据层、应用层。
- 启示：**Financial Chain-of-Thought** 把金融决策固化为可复用的推理链，可用于规则约束 + LLM 的混合决策。

## 6. 本类共性

| 系统 | 记忆 | 反思 | 多模态/数据 | 协作 |
|------|------|------|-------------|------|
| FinAgent | 多样化检索 | 双层反思 | 多模态 | 单/多 agent |
| FinMem | 分层记忆 | 自适应角色 | 多源 | 单 agent |
| FinGPT | — | — | 新闻/财报/社交 | 模型层 |
| QuantAgents | — | — | 市场/新闻 | 4 agent 会议 |
| FinRobot | — | Financial CoT | 多源 | 平台 |

**给我们的三条硬结论**：
1. **金融记忆必须分层**（FinMem/FinAgent 共识），对应我们“冷/温/热 + 分层聚合”。
2. **反思要有双层/自适应**（FinAgent），否则 agent 无法适应市场切换。
3. **Financial CoT + 多 agent 会议**是复合 agent 内部决策的成熟模板。
