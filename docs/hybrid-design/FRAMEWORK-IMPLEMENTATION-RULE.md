# 框架实现规定（Framework Implementation Rule）

> 本规定约束「平台各模块如何编写、如何演进」。核心一句话：**每个模块用一个 `base.py` 定义“契约”，只定义不实现；具体实现继承 `base` 并按场景增强。**

## 1. 总则

1. **base.py = 契约，不是实现**：`base.py` 里只有抽象基类（ABC）、`@abstractmethod`、dataclass、类型标注、枚举、常量与文档字符串；方法体一律 `...` 或 `pass`，不写业务逻辑。
2. **实现继承 base**：每个场景/机制的实现类 `class XxxImpl(XxxBase)`，override 抽象方法，填充具体逻辑。
3. **契约稳定、实现可变**：改 base 即改契约，必须走 `02-decisions-log.md` 的变更记录；新增场景只加实现，不改 base。

## 2. 模块目录结构

```text
masim/platform/
├─ agent/base.py          # AgentRuntime 契约（agent 抽象）
├─ decision/base.py       # DecisionEngine 契约（决策引擎）
├─ composite/base.py      # Aggregator / CompositeOrchestrator 契约（复合）
├─ activation/base.py     # ActivationController / ActivationPolicy / Signal 契约
├─ runtime/base.py        # Clock / Scheduler / SynchronizationPolicy 契约
├─ message/base.py        # MessageBus / Info / Message / SimPacket 契约
├─ state/base.py          # StateStore / Checkpoint 契约
├─ topology/base.py       # Topology 契约
├─ world/base.py          # SharedState 契约（共享环境状态）
├─ registry/base.py       # Registry / IsolationKey 契约
└─ scale/base.py          # ScalePolicy / 降级 / 缓存 / 配额 契约
```

- 每个 `base.py` 内可含多个相关 dataclass + 一个或几个 ABC。
- 具体实现放在同目录或 `impl/` 下，如 `agent/impl_general.py`、`decision/impl_rule.py`。

## 3. base.py 内容规范

每个 `base.py` 必须包含：

1. **模块 docstring**：本模块定位、职责、边界、依赖、用法示例（伪代码）。
2. **dataclass**：字段 + 类型 + 默认值 + 每字段含义注释。
3. **抽象类（ABC）**：
   - 每个抽象方法：签名（参数/返回类型/可能抛出的异常）+ 多行 docstring（目的、参数、返回值、副作用、幂等性、调用时机）。
   - 方法体：`...`。
4. **类型标注**：全部显式标注；集合用 `typing`（`List/Dict/Optional/Protocol` 等）。
5. **枚举**：固定取值用 `Enum`。
6. **不引入重依赖**：base 层只允许 `abc / dataclasses / typing / enum / types`，不 import 具体框架（Ray/LLM SDK 等）。

## 4. 实现规范

1. 实现类继承对应 base，override 抽象方法，可新增私有方法/字段。
2. 不修改 base 的已有签名；如需扩展，优先在实现类加新方法，或按变更记录改 base。
3. 每个实现文件顶部注明：继承自哪个 base、对应哪种场景/机制。

## 5. 一致性要求

- 命名：模块 `snake_case`；类 `PascalCase`；抽象方法 `snake_case` 动词开头（`observe/decide/act/aggregate`）。
- 文档风格：统一用中文注释说明“为什么”，英文保留标识符。
- 异常：契约里声明会抛出的异常类型；实现不得吞掉契约异常。

## 6. 骨架示例（伪代码）

```python
"""模块定位、职责、边界、用法。"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class Decision:
    """一次决策结果。"""
    action: str                 # 动作类型
    payload: Dict[str, Any]     # 动作载荷
    confidence: Optional[float] = None  # 置信度（可空）

class AgentRuntime(ABC):
    """统一递归 agent 抽象：所有 agent（叶子/复合）实现本契约。"""

    @abstractmethod
    async def observe(self, observation: Any, prev_result: Any = None) -> None:
        """把外部观察写入内部状态。不产生决策。"""
        ...

    @abstractmethod
    async def decide(self) -> Decision:
        """基于当前状态产出决策。必须幂等（同状态同决策）。"""
        ...

    @abstractmethod
    def children(self) -> List["AgentRuntime"]:
        """返回子 agent（叶子返回空表）。"""
        ...
```

## 7. 与“最小改造”的关系

- 现有 `masim/simulator/base.py` 等已经“半契约化”（有 `ExecutionClock`、`RoundPhase`、`phase_*` 抽象方法），后续按本规定**抽取/对齐**到 `masim/platform/`，而不是重写。
- 新模块一律先写 `base.py` 契约，再写实现。
