# MASim Demo 详细文档

## 目录

1. [整体架构概览](#1-整体架构概览)
2. [Ray 并行执行原理](#2-ray-并行执行原理)
3. [分层执行模型](#3-分层执行模型)
4. [消息传递与同步机制](#4-消息传递与同步机制)
5. [Demo 执行流程详解](#5-demo-执行流程详解)
6. [配置文件结构](#6-配置文件结构)
7. [运行方式](#7-运行方式)
8. [Ray 执行模式](#8-ray-执行模式)

---

## 1. 整体架构概览

### 1.1 三层抽象模型

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              MASim 三层架构                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Layer 1: Simulator (Driver 进程)                                           │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │  - 管理 Ray 集群连接                                                │      │
│  │  - 创建和管理所有 Persona (Ray Actors)                             │      │
│  │  - 编排仿真生命周期 (setup → run → shutdown)                        │      │
│  │  - 生成 Observation，收集 Action 结果                               │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                              │                                              │
│                              │ Ray Remote Calls (异步)                      │
│                              ▼                                              │
│  Layer 2: Persona (Ray Actor Workers)                                       │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │  PlayerPersona (Actor)         ConductorPersona (Actor)           │      │
│  │  ┌─────────────────────┐       ┌─────────────────────┐            │      │
│  │  │ - operate() 接口    │       │ - cycle() 接口      │            │      │
│  │  │ - 管理 Proxy 生命周期│       │ - receive_responses() │            │      │
│  │  │ - 状态快照/恢复     │       │ - 广播协调决策      │            │      │
│  │  └──────────┬──────────┘       └──────────┬──────────┘            │      │
│  │             │ (内部调用)                   │ (内部调用)             │      │
│  │             ▼                             ▼                       │      │
│  │  Layer 3: Domain Logic (Hidden)                                   │      │
│  │  ┌─────────────────────┐       ┌─────────────────────┐            │      │
│  │  │    BasePlayer       │       │   BaseConductor     │            │      │
│  │  │ - turn() / step()   │       │ - cycle()           │            │      │
│  │  │ - perceive/decide/  │       │ - receive/analyze/  │            │      │
│  │  │   act               │       │   coordinate        │            │      │
│  │  └─────────────────────┘       └─────────────────────┘            │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 核心设计原则

| 原则             | 说明                                                                                       |
|------------------|--------------------------------------------------------------------------------------------|
| **角色语义**     | Player 输出 Action (直接作用于环境)，Conductor 输出 CoordinationDecision (间接影响 Player) |
| **封装隔离**     | Simulator 只与 Persona 交互，Player/Conductor 完全隐藏在内部                               |
| **基础设施解耦** | 通过 Proxy 层处理通信、存储、资源、可观测性                                                |

---

## 2. Ray 并行执行原理

### 2.1 Ray Actor 模型

Ray 是一个分布式计算框架，MASim 使用 Ray Actor 模型实现并行：

```python
# Ray Actor 基本概念
# Actor = 有状态的远程对象，运行在独立的 Worker 进程中

@ray.remote
class MyActor:
    def __init__(self):
        self.state = 0
    
    def method(self, x):
        self.state += x
        return self.state

# 创建 Actor (返回 ActorHandle，不是实例)
actor = MyActor.remote()

# 调用方法 (返回 ObjectRef/Future，不是结果)
future = actor.method.remote(10)

# 获取结果 (阻塞等待)
result = ray.get(future)
```

### 2.2 MASim 中的 Actor 创建

```python
# masim/simulator/base.py 中的实现

def _launch_player_personas(self, personas: Dict[str, PlayerPersona]):
    """将 PlayerPersona 转换为 Ray Actor"""
    
    # 1. 创建 Ray 远程类
    RemotePlayerPersona = ray.remote(PlayerPersona)
    
    handles = {}
    for player_id, persona in personas.items():
        # 2. 创建 Actor 实例 (每个 Player 是独立的 Actor)
        handle = RemotePlayerPersona.options(
            name=f"demo::{player_id}",    # Actor 名称 (可用于获取已有 Actor)
            lifetime="detached",           # Actor 生命周期独立于创建者
            namespace="masim-demo",        # 命名空间隔离
        ).remote(
            player_class=persona._player_class,
            player_config=persona._player_config,
            persona_config=persona._config,
        )
        handles[player_id] = handle
    
    return handles
```

### 2.3 并行执行详解

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Ray 并行执行时序图                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  时间 ─────────────────────────────────────────────────────────────────►    │
│                                                                             │
│  Simulator (Driver):                                                        │
│  ────┬────────────────────────────────────────────────────┬─────────────    │
│      │                                                    │                 │
│      │ [1] 并行发送 operate.remote()                      │ [4] ray.get()   │
│      │     (非阻塞，立即返回 Future)                       │     (阻塞等待)  │
│      │                                                    │                 │
│      ├──► future_1 = handle_1.operate.remote(obs_1)      │                 │
│      ├──► future_2 = handle_2.operate.remote(obs_2)      │                 │
│      └──► future_3 = handle_3.operate.remote(obs_3)      │                 │
│           │          │          │                         │                 │
│           │          │          │                         │                 │
│           ▼          ▼          ▼                         │                 │
│  ─────────────────────────────────────────────────────────┼─────────────    │
│  Worker 1 (Player 1):                                     │                 │
│      [2] ┌─────────────────────────────┐                  │                 │
│          │ perceive() → decide() → act()│ ─────────────────┤                 │
│          └─────────────────────────────┘                  │                 │
│                                                           │                 │
│  Worker 2 (Player 2):                              ───────┤                 │
│      [2] ┌─────────────────────────────┐          │       │                 │
│          │ perceive() → decide() → act()│ ────────┤       │                 │
│          └─────────────────────────────┘          │       │                 │
│                                                   │       │                 │
│  Worker 3 (Player 3):                             │       │                 │
│      [2] ┌─────────────────────────────┐          │       │                 │
│          │ perceive() → decide() → act()│ ────────┘       │                 │
│          └─────────────────────────────┘                  │                 │
│                                                           │                 │
│  [3] 所有 Worker 并行执行完成                       ◄──────┘                 │
│                                                                             │
│  关键点:                                                                    │
│  - [1] operate.remote() 是非阻塞的，立即返回 Future                         │
│  - [2] 三个 Worker 并行执行，互不等待                                       │
│  - [3] 执行完成后结果存储在 Ray Object Store                                │
│  - [4] ray.get() 阻塞直到所有结果就绪                                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.4 代码实现

```python
# masim/simulator/base.py - run_round() 方法

async def run_round(self, round_num: int) -> Dict[str, Any]:
    """执行一个仿真轮次"""
    
    # ========== Phase 1: 生成观测 ==========
    observations = await self.generate_observations(round_num)
    
    # ========== Phase 2: 并行调用所有 PlayerPersona ==========
    operate_futures = {}
    
    for player_id, obs_dict in observations.items():
        handle = self._player_persona_handles[player_id]
        observation = Observation(local=LocalObservation(data={}), notification=obs_dict, round=round_num)
        
        # remote() 调用是非阻塞的！
        # 这里只是把任务提交给 Ray，不等待执行完成
        future = handle.operate.remote(observation, num_steps=1)
        operate_futures[player_id] = future
    
    # 此时所有 Player 已经开始并行执行！
    
    # ========== Phase 3: 等待所有结果 ==========
    turn_results = {}
    for player_id, future in operate_futures.items():
        # ray.get() 阻塞等待该 Actor 完成
        turn_result = ray.get(future)
        turn_results[player_id] = turn_result
    
    # 也可以一次性等待所有:
    # all_results = ray.get(list(operate_futures.values()))
    
    # ========== Phase 4: Coordinator 协调 (if any) ==========
    # Note: Coordinator is just a Player with role='coordinator'
    # Coordination is done via topology-driven message passing
    # No special receive_coordination method needed
    
    return round_results
```

---

## 3. 分层执行模型

### 3.1 执行层次

```
┌────────────┬───────────────────┬────────────┬────────────────────────────────┐
│   Level    │      Entity       │    Term    │         Description            │
├────────────┼───────────────────┼────────────┼────────────────────────────────┤
│    L1      │    Simulator      │   round    │ 一个完整仿真周期               │
│            │   (Driver)        │            │ 包含所有 Persona 的执行        │
├────────────┼───────────────────┼────────────┼────────────────────────────────┤
│    L2      │  PlayerPersona    │   operate  │ Simulator 调用的接口           │
│            │  (Ray Actor)      │            │ 内部调用 Player.turn()         │
├────────────┼───────────────────┼────────────┼────────────────────────────────┤
│    L3      │     Player        │   turn     │ 多步执行循环                   │
│            │    (Hidden)       │            │ for i in range(num_steps):     │
│            │                   │            │     step()                     │
├────────────┼───────────────────┼────────────┼────────────────────────────────┤
│    L4      │     Player        │   step     │ 原子操作                       │
│            │    (Hidden)       │            │ perceive → decide → act        │
├────────────┼───────────────────┼────────────┼────────────────────────────────┤
│    L2      │ ConductorPersona  │   cycle    │ 协调周期                       │
│            │  (Ray Actor)      │            │ receive → analyze → coordinate │
└────────────┴───────────────────┴────────────┴────────────────────────────────┘
```

### 3.2 Player 执行流程

```python
# masim/player/base.py

class BasePlayer:
    async def turn(self, observation: Observation, num_steps: int = 1) -> TurnResult:
        """执行一个 turn (多个 step 的循环)"""
        
        step_results = []
        prev_result = None
        current_observation = observation
        
        # 多步循环
        for _ in range(num_steps):
            # 每个 step 可以使用上一步的结果
            step_result = await self.step(current_observation, prev_result)
            step_results.append(step_result)
            prev_result = step_result
        
        return TurnResult(
            step_results=step_results,
            final_action=step_results[-1].action if step_results else None,
        )
    
    async def step(self, observation: Observation, prev_result=None) -> StepResult:
        """执行一个原子 step: perceive → decide → act"""
        
        # 1. 感知: 处理观测数据
        await self.perceive(observation, prev_result)
        
        # 2. 决策: 基于当前状态做决定
        decision_payload = await self.decide()
        
        # 3. 行动: 将决策转换为 Action
        action = await self.act(decision_payload)
        
        return StepResult(action=action, decision_payload=decision_payload)
```

### 3.3 Conductor 执行流程

```python
# masim/conductor/base.py

class BaseConductor:
    async def cycle(self) -> CycleResult:
        """执行一个协调周期"""
        
        # 1. 获取缓冲的 Action
        actions = self._action_buffer.copy()
        self._action_buffer.clear()
        
        # 2. 接收: 处理所有 Action
        await self.receive_responses(actions)
        
        # 3. 分析: 分析当前状态
        analysis_result = await self.analyze()
        
        # 4. 协调: 生成协调决策
        decision = await self.coordinate(analysis_result)
        
        return CycleResult(decision=decision, actions_processed=len(actions))
```

---

## 4. 消息传递与同步机制

### 4.1 Player → Conductor 消息流

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Player → Conductor 消息传递                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Player 1 ──┬─► Action { type: "submit_price", payload: {price: 101.5} }    │
│             │                                                               │
│  Player 2 ──┼─► Action { type: "submit_price", payload: {price: 99.2} }     │
│             │                                                               │
│  Player 3 ──┴─► Action { type: "submit_price", payload: {price: 100.8} }    │
│                                    │                                        │
│                                    ▼                                        │
│                    ┌───────────────────────────────┐                        │
│                    │      Conductor (Market)       │                        │
│                    │                               │                        │
│                    │  _action_buffer = [           │                        │
│                    │    Action(price=101.5),       │                        │
│                    │    Action(price=99.2),        │                        │
│                    │    Action(price=100.8),       │                        │
│                    │  ]                            │                        │
│                    │                               │                        │
│                    │  cycle():                     │                        │
│                    │    receive_responses()          │                        │
│                    │    analyze() → avg=100.5      │                        │
│                    │    coordinate() → decision    │                        │
│                    └───────────────────────────────┘                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Conductor → Player 广播

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Conductor → Player 广播机制                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                    ┌───────────────────────────────┐                        │
│                    │      Conductor (Market)       │                        │
│                    │                               │                        │
│                    │  CoordinationDecision {       │                        │
│                    │    type: "price_broadcast",   │                        │
│                    │    scope: GLOBAL,             │                        │
│                    │    parameters: {              │                        │
│                    │      avg_price: 100.5         │                        │
│                    │    }                          │                        │
│                    │  }                            │                        │
│                    └───────────────┬───────────────┘                        │
│                                    │                                        │
│                 ┌──────────────────┼──────────────────┐                     │
│                 │                  │                  │                     │
│                 ▼                  ▼                  ▼                     │
│            ┌─────────┐       ┌─────────┐       ┌─────────┐                  │
│            │Player 1 │       │Player 2 │       │Player 3 │                  │
│            │         │       │         │       │         │                  │
│            │state:   │       │state:   │       │state:   │                  │
│            │last_    │       │last_    │       │last_    │                  │
│            │coord=   │       │coord=   │       │coord=   │                  │
│            │{avg:    │       │{avg:    │       │{avg:    │                  │
│            │ 100.5}  │       │ 100.5}  │       │ 100.5}  │                  │
│            └─────────┘       └─────────┘       └─────────┘                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.3 同步点详解

```python
# Simulator 中的同步点

async def run_round(self, round_num):
    
    # ===== 同步点 1: 等待所有 Player 完成 =====
    operate_futures = {}
    for player_id, handle in self._player_persona_handles.items():
        future = handle.operate.remote(observation)  # 非阻塞
        operate_futures[player_id] = future
    
    # 阻塞等待所有 Player 完成
    for player_id, future in operate_futures.items():
        turn_result = ray.get(future)  # <-- 同步点
    
    # ===== 同步点 2: 等待 Conductor 接收 Actions =====
    ray.get(
        self._conductor_persona_handle.receive_responses.remote(actions)
    )  # <-- 同步点
    
    # ===== Coordinator 协调 (如果有的话) =====
    # Note: Coordinator 只是具有 role='coordinator' 的 Player
    # 协调通过拓扑驱动的消息传递完成
```

### 4.4 连接验证

```python
# 使用 ConnectionValidator 确保只有连接的实体可以通信

from masim.utils.config import load_config, ConnectionValidator

config = load_config("configs/Demo/simulation.yml")
validator = ConnectionValidator(config)

# 验证连接
validator.validate_send("market", "investor_1")    # ✓ OK
validator.validate_send("investor_1", "market")    # ✓ OK
validator.validate_send("investor_1", "investor_2")  # ✗ ConnectionError!
```

---

## 5. Demo 执行流程详解

### 5.1 完整流程图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Demo 完整执行流程                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [初始化阶段]                                                               │
│  ┌─────────────────────────────────────────────────────────────────┐        │
│  │  1. load_config("configs/Demo/simulation.yml")                  │        │
│  │     ├── !include players.yml                                    │        │
│  │     ├── !include conductor.yml                                  │        │
│  │     └── !include topology.yml                                   │        │
│  │                                                                 │        │
│  │  2. ConnectionValidator(config) 构建连接矩阵                    │        │
│  │     market → [investor_1, investor_2, investor_3]               │        │
│  │     investor_1 → [market]                                       │        │
│  │     investor_2 → [market]                                       │        │
│  │     investor_3 → [market]                                       │        │
│  │                                                                 │        │
│  │  3. 创建 ConductorPersona (market)                              │        │
│  │     └── 内部创建 SimpleMarket 实例                               │        │
│  │                                                                 │        │
│  │  4. 创建 3 个 PlayerPersona (investor_1, 2, 3)                  │        │
│  │     └── 每个内部创建 SimpleInvestor 实例                         │        │
│  └─────────────────────────────────────────────────────────────────┘        │
│                                                                             │
│  [Round 1-10 循环]                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐        │
│  │                                                                 │        │
│  │  ┌─────────────────────────────────────────────────────────┐    │        │
│  │  │ Step A: Market → Investors (广播当前均价)                │    │        │
│  │  │                                                         │    │        │
│  │  │   for investor_id in [investor_1, investor_2, investor_3]:   │        │
│  │  │       validator.validate_send("market", investor_id)    │    │        │
│  │  │       observation = Observation(local=LocalObservation(data={}), notification={avg_price: 100.0}, round=r)│    │        │
│  │  │       # 发送观测到 Investor                              │    │        │
│  │  └─────────────────────────────────────────────────────────┘    │        │
│  │                         │                                       │        │
│  │                         ▼                                       │        │
│  │  ┌─────────────────────────────────────────────────────────┐    │        │
│  │  │ Step B: 每个 Investor 执行 operate()                    │    │        │
│  │  │                                                         │    │        │
│  │  │   turn_result = await persona.operate(observation)      │    │        │
│  │  │                                                         │    │        │
│  │  │   内部执行:                                              │    │        │
│  │  │   ┌─────────────────────────────────────────────────┐   │    │        │
│  │  │   │ perceive():                                     │   │    │        │
│  │  │   │   state["market_avg"] = obs.data["avg_price"]   │   │    │        │
│  │  │   │                                                 │   │    │        │
│  │  │   │ decide():                                       │   │    │        │
│  │  │   │   local_price = state["local_price"]            │   │    │        │
│  │  │   │   random_factor = uniform(-0.1, 0.1)            │   │    │        │
│  │  │   │   new_price = local_price + avg * random_factor │   │    │        │
│  │  │   │   state["local_price"] = new_price              │   │    │        │
│  │  │   │                                                 │   │    │        │
│  │  │   │ act():                                          │   │    │        │
│  │  │   │   return Action(type="submit_price",            │   │    │        │
│  │  │   │                 payload={price: new_price})     │   │    │        │
│  │  │   └─────────────────────────────────────────────────┘   │    │        │
│  │  └─────────────────────────────────────────────────────────┘    │        │
│  │                         │                                       │        │
│  │                         ▼                                       │        │
│  │  ┌─────────────────────────────────────────────────────────┐    │        │
│  │  │ Step C: Investors → Market (提交价格)                   │    │        │
│  │  │                                                         │    │        │
│  │  │   validator.validate_send(investor_id, "market")        │    │        │
│  │  │   market._conductor.on_action_received(action)          │    │        │
│  │  └─────────────────────────────────────────────────────────┘    │        │
│  │                         │                                       │        │
│  │                         ▼                                       │        │
│  │  ┌─────────────────────────────────────────────────────────┐    │        │
│  │  │ Step D: Market 执行 cycle()                             │    │        │
│  │  │                                                         │    │        │
│  │  │   cycle_result = await market.cycle()                   │    │        │
│  │  │                                                         │    │        │
│  │  │   内部执行:                                              │    │        │
│  │  │   ┌─────────────────────────────────────────────────┐   │    │        │
│  │  │   │ receive_responses():                              │   │    │        │
│  │  │   │   prices = [action.payload["price"] for ...]    │   │    │        │
│  │  │   │   state["prices"] = prices                      │   │    │        │
│  │  │   │                                                 │   │    │        │
│  │  │   │ analyze():                                      │   │    │        │
│  │  │   │   avg_price = sum(prices) / len(prices)         │   │    │        │
│  │  │   │   return {"avg_price": avg_price}               │   │    │        │
│  │  │   │                                                 │   │    │        │
│  │  │   │ coordinate():                                   │   │    │        │
│  │  │   │   return CoordinationDecision(                  │   │    │        │
│  │  │   │     type="price_broadcast",                     │   │    │        │
│  │  │   │     parameters={"avg_price": avg_price}         │   │    │        │
│  │  │   │   )                                             │   │    │        │
│  │  │   └─────────────────────────────────────────────────┘   │    │        │
│  │  └─────────────────────────────────────────────────────────┘    │        │
│  │                         │                                       │        │
│  │                         ▼                                       │        │
│  │  ┌─────────────────────────────────────────────────────────┐    │        │
│  │  │ Step E: 更新 avg_price，进入下一轮                      │    │        │
│  │  │                                                         │    │        │
│  │  │   avg_price = cycle_result.decision.parameters["avg"]   │    │        │
│  │  └─────────────────────────────────────────────────────────┘    │        │
│  │                                                                 │        │
│  └─────────────────────────────────────────────────────────────────┘        │
│                                                                             │
│  [结束阶段]                                                                 │
│  ┌─────────────────────────────────────────────────────────────────┐        │
│  │  打印最终结果:                                                   │        │
│  │    Final average price: xxx.xx                                  │        │
│  │    investor_1: local_price = xxx.xx                             │        │
│  │    investor_2: local_price = xxx.xx                             │        │
│  │    investor_3: local_price = xxx.xx                             │        │
│  │                                                                 │        │
│  │  Shutdown 所有 Persona                                          │        │
│  └─────────────────────────────────────────────────────────────────┘        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. 配置文件结构

### 6.1 文件组织

```
configs/Demo/
├── simulation.yml    # 主配置 (使用 !include)
├── players.yml       # Player 定义
├── conductor.yml     # Conductor 定义
└── topology.yml      # 连接拓扑
```

### 6.2 topology.yml 连接配置

```yaml
# 定义谁可以向谁发送消息
connections:
  # Market → 所有 Investor
  market:
    - investor_1
    - investor_2
    - investor_3
  
  # 每个 Investor → Market
  investor_1:
    - market
  investor_2:
    - market
  investor_3:
    - market

# 可视化
#         investor_1 ──┐
#                      │
#         investor_2 ──┼──► market ──┬──► investor_1
#                      │             ├──► investor_2
#         investor_3 ──┘             └──► investor_3
```

---

## 7. 运行方式

MASim Demo 支持两种运行模式，主要区别在于运行结束后 Ray Dashboard 是否可用。

### 7.1 命令行用法

```bash
# 必须使用 -c 指定配置文件
python examples/Demo/run_simple_simulation.py -c configs/Demo/simulation.yml
```

### 7.2 持久化模式（推荐）

在运行仿真之前先启动 Ray 集群，这样仿真结束后 Dashboard 仍然可用，可以查看运行日志和历史。

**启动步骤：**

```bash
# 步骤 1: 先启动 Ray 集群（独立进程）
ray start --head

# 步骤 2: 运行仿真
cd /path/to/multiagent-simulation
python examples/Demo/run_simple_simulation.py -c configs/Demo/simulation.yml

# 步骤 3: 仿真结束后，Dashboard 仍然可用！
open http://127.0.0.1:8265

# 步骤 4: 检查完毕后，手动关闭 Ray
ray stop
```

**运行输出：**

```
23:50:01 [INFO] ============================================================
23:50:01 [INFO] Simple Price Averaging Simulation (Ray Mode)
23:50:01 [INFO] ============================================================
23:50:01 [INFO] [0] Initializing Ray cluster...
23:50:01 [INFO]     Connected to existing Ray cluster    ← 连接到已有集群
23:50:01 [INFO]     Namespace: masim-demo
23:50:01 [INFO]     Dashboard: http://127.0.0.1:8265
...
23:50:10 [INFO] [5] Shutting down Ray Actors...
23:50:10 [INFO]     All actors terminated
23:50:10 [INFO]     Ray cluster still running - Dashboard available at http://127.0.0.1:8265
23:50:10 [INFO]     To stop Ray: ray stop
23:50:10 [INFO] ============================================================
23:50:10 [INFO] Simulation Complete!
23:50:10 [INFO] ============================================================
```

**结果：**

| 时机          | Dashboard      | 日志             | Ray 集群 |
|---------------|----------------|------------------|----------|
| 运行中        | ✅ 可访问       | ✅ 实时显示       | ✅ 运行中 |
| 运行结束后    | ✅ **仍可访问** | ✅ **可查看历史** | ✅ 仍运行 |
| 手动 ray stop | ❌ 不可访问     | ❌ 无法查看       | ❌ 已关闭 |

### 7.3 直接模式

不预先启动 Ray 集群，直接运行仿真。仿真结束后 Ray 随 Python 进程一起退出。

**启动步骤：**

```bash
# 直接运行，不预先启动 Ray
cd /path/to/multiagent-simulation
python examples/Demo/run_simple_simulation.py -c configs/Demo/simulation.yml

# 仿真结束后 Dashboard 不可用
```

**运行输出：**

```
23:50:01 [INFO] ============================================================
23:50:01 [INFO] Simple Price Averaging Simulation (Ray Mode)
23:50:01 [INFO] ============================================================
23:50:01 [INFO] [0] Initializing Ray cluster...
23:50:02 [INFO]     Started new Ray cluster (will stop when script exits)    ← 新启动的集群
23:50:02 [INFO]     TIP: For persistent dashboard, run 'ray start --head' before this script
23:50:02 [INFO]     Namespace: masim-demo
23:50:02 [INFO]     Dashboard: http://127.0.0.1:8265
...
23:50:10 [INFO] [5] Shutting down Ray Actors...
23:50:10 [INFO]     All actors terminated
23:50:10 [INFO]     Ray cluster still running - Dashboard available at http://127.0.0.1:8265
23:50:10 [INFO]     To stop Ray: ray stop
23:50:10 [INFO] ============================================================
23:50:10 [INFO] Simulation Complete!
23:50:10 [INFO] ============================================================

# 脚本退出后，Ray 进程也退出
```

**结果：**

| 时机       | Dashboard      | 日志           | Ray 集群 |
|------------|----------------|----------------|----------|
| 运行中     | ✅ 可访问       | ✅ 实时显示     | ✅ 运行中 |
| 运行结束后 | ❌ **不可访问** | ❌ **无法查看** | ❌ 已关闭 |

### 7.4 两种模式对比

| 特性                 | 持久化模式 (ray start) | 直接模式        |
|----------------------|------------------------|-----------------|
| **Dashboard 持久化** | ✅ 是                   | ❌ 否            |
| **运行后可查日志**   | ✅ 是                   | ❌ 否            |
| **需要预先命令**     | ✅ ray start --head     | ❌ 不需要        |
| **需要手动关闭**     | ✅ ray stop             | ❌ 自动关闭      |
| **适用场景**         | 调试、分析、多次运行   | 快速测试、CI/CD |

### 7.5 查看 Ray 状态

```bash
# 查看 Ray 集群状态
ray status

# 查看所有 Actor
ray list actors

# 实时查看日志流
ray logs

# 手动停止 Ray
ray stop
```

### 7.6 日志文件位置

Ray 将日志写入文件系统，即使 Dashboard 不可用也可以查看：

```bash
# 查看 Ray 日志目录
ls /tmp/ray/session_latest/logs/

# 查看特定 Worker 的日志
cat /tmp/ray/session_latest/logs/worker-*.log

# 实时跟踪日志
tail -f /tmp/ray/session_latest/logs/worker-*.log
```

---

## 8. Ray 执行模式

**MASim 框架强制使用 Ray 模式**。所有 Player 和 Conductor 都作为 Ray Actor 在独立的 Worker 进程中并行运行。

### 8.1 为什么强制使用 Ray？

| 设计考量       | 说明                                           |
|----------------|------------------------------------------------|
| **真正的并行** | 多个 Player 在独立进程中同时执行，利用多核 CPU |
| **故障隔离**   | 一个 Actor 崩溃不会影响其他 Actor              |
| **可扩展性**   | 可以无缝扩展到多台机器组成的集群               |
| **状态隔离**   | 每个 Actor 有独立的内存空间，天然隔离          |
| **一致性**     | 开发环境和生产环境使用相同的执行模型           |

### 8.2 执行架构

当你运行 `run_simple_simulation.py` 时：

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                             Ray 集群                                          │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌───────────────────────┐                                                    │
│  │   Driver 进程         │  ← 你的终端运行这个                                │
│  │   (Simulator)         │  ← 编排所有 Actor                                  │
│  └───────────┬───────────┘                                                    │
│              │                                                                │
│              │ ray.remote() 调用 (异步、非阻塞)                               │
│              │                                                                │
│  ┌───────────┴───────────────────────────────────────────────────────┐        │
│  │                  后台 Worker 进程 (Ray 自动管理)                   │        │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────────┐  │        │
│  │  │  Worker 1   │  │  Worker 2   │  │  Worker 3   │  │ Worker 4 │  │        │
│  │  │ Investor 1  │  │ Investor 2  │  │ Investor 3  │  │  Market  │  │        │
│  │  │ (Actor)     │  │ (Actor)     │  │ (Actor)     │  │ (Actor)  │  │        │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └──────────┘  │        │
│  │                                                                   │        │
│  │  ↑ 并行执行！每个 Actor 在独立进程中运行                          │        │
│  └───────────────────────────────────────────────────────────────────┘        │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘
```

### 8.3 只需要一个终端

虽然有多个进程在运行，但你**只需要打开一个终端**：

```bash
# 只需运行这一个命令
cd /path/to/multiagent-simulation
python examples/Demo/run_simple_simulation.py
```

Ray 会自动：
1. **启动本地集群**（如果没有运行中的集群）
2. **创建 Worker 进程**（在后台，不可见）
3. **部署 Actor** 到 Worker
4. **管理进程间通信**
5. **收集结果**返回给 Driver

### 8.4 代码中的 Ray 使用

```python
import ray

# 1. 初始化 Ray 集群
ray.init(namespace="masim-demo")

# 2. 创建 Ray Actor 类
RemotePlayerPersona = ray.remote(PlayerPersona)

# 3. 启动 Actor (每个 Actor 在独立 Worker 进程中)
handle = RemotePlayerPersona.options(
    name="demo::investor_1",      # Actor 名称
    namespace="masim-demo",       # 命名空间隔离
    lifetime="detached",          # 独立生命周期
).remote(
    player_class=SimpleInvestor,
    player_config=config,
)

# 4. 初始化 Actor
ray.get(handle.initialize.remote())

# 5. 并行调用 (非阻塞！)
futures = {}
for investor_id, handle in investor_handles.items():
    # remote() 立即返回 Future，不等待执行完成
    future = handle.operate.remote(observation, num_steps=1)
    futures[investor_id] = future

# 此时所有 Actor 并行执行中！

# 6. 收集结果 (阻塞等待)
for investor_id, future in futures.items():
    result = ray.get(future)  # 等待结果
```

### 8.5 并行执行时序

```
时间 ─────────────────────────────────────────────────────────────────────►

Driver:     [发送观测]────────────────────────────────────[收集结果]──[Conductor]
                │                                              ↑
                │ operate.remote() (非阻塞)                    │ ray.get()
                │                                              │
                ├──────────────────────────────────────────────┤
                │                                              │
Investor 1: ───[perceive → decide → act]─────────────────────►│
Investor 2: ───[perceive → decide → act]─────────────────────►│  ← 并行！
Investor 3: ───[perceive → decide → act]─────────────────────►│
                │                                              │
                └──────────────────────────────────────────────┘
                  ↑
                  三个 Investor 同时执行，互不等待
```

### 8.6 查看 Ray Dashboard

运行时可以打开 Ray Dashboard 查看 Actor 状态：

```
http://127.0.0.1:8265
```

Dashboard 显示：
- 集群状态（CPU、内存使用）
- 所有 Actor 列表
- 任务执行情况
- 日志输出

---

## 附录: 关键类图

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   Simulator     │      │  PlayerPersona  │      │ConductorPersona │
├─────────────────┤      ├─────────────────┤      ├─────────────────┤
│ - config        │      │ - _player       │      │ - _conductor    │
│ - round_clock   │      │ - _player_class │      │ - _conductor_   │
│ - _player_      │◄────►│ - _player_config│      │   class         │
│   persona_      │      ├─────────────────┤      ├─────────────────┤
│   handles       │      │ + initialize()  │      │ + initialize()  │
│ - _conductor_   │◄────►│ + operate()     │      │ + cycle()       │
│   persona_      │      │ + shutdown()    │      │ + receive_      │
│   handle        │      │ + get_state_    │      │   actions()     │
├─────────────────┤      │   snapshot()    │      │ + shutdown()    │
│ + setup()       │      └────────┬────────┘      └────────┬────────┘
│ + run_round()   │               │                        │
│ + run()         │               │ (internal)             │ (internal)
│ + shutdown()    │               ▼                        ▼
└─────────────────┘      ┌─────────────────┐      ┌─────────────────┐
                         │   BasePlayer    │      │  BaseConductor  │
                         ├─────────────────┤      ├─────────────────┤
                         │ - _state        │      │ - _state        │
                         │ - config        │      │ - config        │
                         ├─────────────────┤      ├─────────────────┤
                         │ + turn()        │      │ + cycle()       │
                         │ + step()        │      │ + receive_      │
                         │ + perceive()    │      │   actions()     │
                         │ + decide()      │      │ + analyze()     │
                         │ + act()         │      │ + coordinate()  │
                         └─────────────────┘      └─────────────────┘
```
