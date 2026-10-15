"""Composite（复合 agent 内部编排与聚合）契约。

定位：
    复合 agent 的“内部结构”：子结果聚合（Aggregator）与内部编排（CompositeOrchestrator）。
    复合 agent 对外仍是 AgentRuntime（见 agent/base.py），内部用本契约组织子 agent。

职责边界：
    - 只管“怎么把子结果聚合成父决策依据”与“子 agent 内部怎么编排”。
    - 不管子 agent 本身怎么决策（那是 DecisionEngine 的事）。
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ChildResult:
    """一个子 agent 的决策结果（供聚合）。

    字段：
        child_id:   子 agent 身份。
        decision:   子决策结果（Any，通常为 Decision）。
        confidence: 子决策置信度（可空）。
        evidence:   子决策依据/溯源引用（可空）。
        meta:       扩展信息（耗时、降级标记等）。
    """

    child_id: str
    decision: Any
    confidence: Optional[float] = None
    evidence: Optional[Any] = None
    meta: Dict[str, Any] = field(default_factory=dict)


class Aggregator(ABC):
    """子结果聚合器契约（可插拔）。

    不同场景可用不同聚合：统计聚合（均值/分位/多数）、LLM 摘要聚合、层级聚合等。
    """

    @abstractmethod
    def aggregate(self, child_results: List[ChildResult]) -> Any:
        """把子结果聚合成一个汇总对象。

        返回：聚合摘要。建议至少包含「统计量 + 关键离群样本 + 溯源引用」三要素，
              以便父 agent 既能基于摘要决策，又能回溯到具体子结果。
        幂等性：相同输入应产出相同汇总。
        """
        ...


class CompositeOrchestrator(ABC):
    """复合 agent 内部编排器契约。

    定义“哪些子 agent 跑、以什么顺序/并行度跑”。可作为 Workflow/Harness 的薄封装。
    """

    @abstractmethod
    async def run(self, context: Any, children: List[Any]) -> List[ChildResult]:
        """按编排策略执行子 agent，返回其决策结果列表。

        参数：
            context: 父 agent 收到的观察/上下文。
            children: 子 agent（顺序即 children() 顺序）。
        返回：与 children 一一对应的 ChildResult。
        实现约束：子 agent 的调用顺序/并行度由本方法决定，但必须返回完整结果。
        """
        ...
