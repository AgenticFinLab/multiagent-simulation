# 模拟器与建模方法：采用哪些经验

[证据入口](README.md) · [运行框架与工程机制](02-runtime-and-infrastructure.md)

## 1. OASIS：环境能力与信息分发

OASIS 官方资料将动态社交网络、内容环境、行动集合和推荐系统放入模拟器，并报告百万用户规模；README 也按主体数、激活概率和时间步讨论调用成本。[官方仓库](https://github.com/camel-ai/oasis)、[论文](https://arxiv.org/abs/2411.11581)

**对本稿的启发：** 将可用行动和信息分发机制作为环境能力，主体决定如何使用它们。规模描述同时记录总主体与实际激活，避免只比较注册人数。

**采用位置：** [环境能力合同](../05-environment-and-actions.md)、[路由与可见性](../07-time-and-communication.md)、[负载分解](../08-execution-and-scaling.md)。

**适用边界：** 社交平台的推荐和行动语义属于领域模型。本方案借鉴其组件组织，具体能力由环境定义；本系统容量需要结合调用频率、硬件和活动复杂度独立测量。

## 2. AgentSociety：规模需要完整运行环境

AgentSociety 论文报告超过一万主体与五百万次交互，其研究对象包括主体之间及主体与环境的交互。这些数值为论文报告结果。[AgentSociety 论文](https://arxiv.org/abs/2502.08691)

AgentSociety 2 当前架构按批次提交 Ray Task，在任务内并发推进主体，再执行环境 step。主体可从持久工作区重建，运行服务通过代理连接。[AgentSociety 2 架构](https://agentsociety2.readthedocs.io/en/latest/architecture.html)

**对本稿的启发：** 长期身份与执行对象分离，按活跃工作装载；环境、模型访问和记录可作为共享服务。其第二版工程资料与前述论文实验分开引用，不能将两个版本的实现和性能直接合并。

**采用位置：** [共享执行](../08-execution-and-scaling.md)、[状态恢复](../09-state-and-recovery.md)。

**适用边界：** 本方案增加持续活动、固定读取版本与联合提交，这种组合的成本仍需验证。进程内模型控制还需要与端点总配额协调。

## 3. Mesa：模型组件与激活方式分开

Mesa 官方概览分别组织模型、主体、空间、分析和可视化，提供主体激活与 Model 上的事件调度能力。[Mesa 概览](https://mesa.readthedocs.io/stable/overview.html)

**对本稿的启发：** 使用者通过模型组件声明世界和主体，运行层提供激活与记录；领域模型无需继承某个金融模拟器。

**采用位置：** [模型装配](../03-model-and-contracts.md)与[环境扩展](../05-environment-and-actions.md)。

**适用边界：** 这支持职责拆分的合理性，不能证明 Ray、MAF 与数据库组合的性能。本文没有把 Mesa 作为第二套运行依赖。

## 4. Generative Agents：记忆是一种可选择的机制

该工作组织记忆流、检索、反思与规划，检索考虑相关性、新近性和重要性。[论文相关正文](https://arxiv.org/html/2304.03442v2)

**对本稿的启发：** 将主体记忆保存、检索和反思分别建模，与当前活动会话区分。不同主体可以使用不同记忆机制，检索和摘要产物需要来源。

**采用位置：** [主体与记忆](../04-agents-and-memory.md)。

**适用边界：** 反思和摘要改变后续输入，也增加调用成本。它们是可配置的行为机制，系统不保证加入这些组件就提升真实行为一致性。

## 5. 环境参与的社会模拟形式化

Li、Tao 的立场论文把环境、网络、情境、主体心理状态、观察、行动、初始分布、调度、可见性和转移共同纳入模拟器定义。[Definition 4.1](https://arxiv.org/html/2603.00113v2)

**对本稿的启发：** 用它检查模型描述有没有遗漏主体之外的机制。对应关系如下：

| 概念 | 本方案中的表达 |
|---|---|
| 环境、网络与情境 | 环境模块、关系模块、定时或外部输入 |
| 主体状态与观察 | ActorState、MemoryPolicy、ActorView |
| 行动与决策 | 能力合同、BehaviorDefinition、SimulationRequest |
| 初始分布 | PopulationDefinition 与初始化记录 |
| 调度与可见性 | Scheduler、消息投递、ObservationBuilder |
| 转移机制 | 环境后果、主体更新与联合提交 |

该对应是本方案的工程解释。论文以固定 N 和 T 陈述定义，本设计另外显式表示活动和运行资源，也允许通过生命周期操作改变活跃主体集合。无需让理论元组与软件类逐项一一对应。

**适用边界：** 形式化有助于说明职责和研究对象，不能证明选用 MAF、Ray 或保守阶段算法最优，更不能替代领域有效性研究。

## 6. 其他相关工作

[hybrid-design/existing-work](../../hybrid-design/existing-work/README.md) 还收录了 Project Sid、TwinMarket、MarketSim、EconAgent 等社会与金融模拟工作，可为活动组织、分层行为和领域环境提供参考。

引入具体机制前，应核对其论文、源码版本和实验条件，明确需要适配的接口与验证要求。
