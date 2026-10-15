# 04 · 金融 LLM agent（领域层参考）

> 只作领域参考；核心价值是“记忆/反思/市场智能”怎么设计，映射到平台记忆与决策引擎。

## 1. FinAgent（多模态金融基础 agent）

- 核心：**市场智能模块**（数值 + 文本 + 视觉）、**双层反思**、**多样化记忆检索**。
- 启示：金融 agent 的“感知-反思-记忆”三件套；双层反思用于快速适应市场动态。

## 2. FinMem（分层记忆 + 角色）

- 三个模块：Character（角色定制）、**Memory（分层消息处理）**、Decision-making。
- 启示：**金融记忆必须分层**（高频行情 / 日度事件 / 长期风格），不能一条扁平记忆流；自适应角色应对波动。

## 3. FinGPT（开源金融大模型）

- 核心：开源 FinLLM；**RLSP（Reinforcement Learning from Stock Prices）**把预测与市场结果对齐；LoRA 微调；实时数据管道。
- 启示：金融专用小模型可做信号/情绪抽取，降低成本——属于“模型层”，我们可选。

## 4. QuantAgents（模拟交易多 agent）

- 四个 agent：模拟交易分析师、风控分析师、市场新闻分析师、经理，通过多轮会议协作；定位“不冒真实风险的策略/场景评估”。
- 启示：“分析师 + 风控 + 经理会议”是复合 agent 内部 supervisor 的范本。

## 5. FinRobot（金融 AI agent 平台）

- 四层：Financial AI Agents 层（**Financial CoT**：收集数据→分析→规划→执行）、LLM 算法层、数据层、应用层。
- 启示：Financial CoT 把金融决策固化为可复用推理链，可用于规则约束 + LLM 混合。

## 6. 汇总到平台契约

| 机制 | 平台模块 |
|------|----------|
| 分层记忆 / 双层反思 / 记忆检索 | `StateStore` + `KnowledgeStore`（冷温热） |
| 多模态市场智能 | `DecisionEngine` 的领域实现（不进内核） |
| Financial CoT / 会议协作 | `CompositeOrchestrator` + `Aggregator` |
| 角色定制 | `AgentRuntime` + 使用者 persona |
