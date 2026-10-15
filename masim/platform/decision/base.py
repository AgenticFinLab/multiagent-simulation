"""DecisionEngine 契约。

定位：
    把「观察 → 决策」这一步具体化的引擎。AgentRuntime.decide() 内部委托给本引擎。

职责边界：
    - 只管“怎么决策”，不管“谁该动”（activation）、“什么时候动”（runtime）、“消息怎么传”（message）。

实现规范：
    - 每种决策机制继承 DecisionEngine，实现 decide()。
    - 引擎应能声明其成本/延迟预算是否满足（supports_budget），否则由上层降级。
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class EngineKind(str, Enum):
    """决策引擎种类（用于路由/统计/降级选择）。"""

    RULE = "rule"        # 纯规则 / 确定性逻辑
    LLM = "llm"          # 大模型决策
    RAG = "rag"          # 检索增强决策
    COMPOSITE = "composite"  # 复合（内部编排多个子引擎/子 agent）


@dataclass
class DecisionContext:
    """一次决策所需的上下文（观察 + 预算 + 元信息）。

    字段：
        observation: 本轮观察（结构化/文本均可）。
        budget:      本决策允许的预算上限（token / 次数 / 成本，单位由实现定义）。
        deadline:    本决策的截止时间（逻辑时间戳或单调时钟，可空）。
        meta:        扩展元信息（模型版本、缓存策略、降级链等）。
    """

    observation: Any
    budget: Optional[Any] = None
    deadline: Optional[Any] = None
    meta: Dict[str, Any] = field(default_factory=dict)


class DecisionEngine(ABC):
    """决策引擎契约。"""

    @property
    @abstractmethod
    def kind(self) -> EngineKind:
        """返回引擎种类。"""
        ...

    @abstractmethod
    async def decide(self, context: DecisionContext) -> Any:
        """基于上下文产出决策结果。

        参数：
            context: 观察 + 预算 + 截止时间 + 元信息。
        返回：决策结果（通常是 agent/base.py 的 Decision；复合引擎可返回聚合对象）。
        抛出：
            BudgetExceeded / DeadlineExceeded —— 表示本引擎在给定预算/截止内无法完成，
            由上层决定是否降级（见 scale/base.py 的 DegradationPolicy）。
        幂等性：相同 context（且模型参数固定）应产出相同结果。
        """
        ...

    @abstractmethod
    def supports(self, budget: Optional[Any], deadline: Optional[Any]) -> bool:
        """判断本引擎在给定预算/截止下是否可用（用于路由与降级预判）。"""
        ...
