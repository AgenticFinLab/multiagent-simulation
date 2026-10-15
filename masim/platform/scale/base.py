"""ScalePolicy（规模化与成本控制）契约。

定位：
    平台的“规模与成本策略层”：引擎配比、活跃子集/抽样、缓存、降级链、配额、成本归因。

职责边界：
    - 只定义策略接口与数据结构，不绑定具体 LLM 供应商。
    - 实际转发/限流/缓存交给 LLM 网关（LiteLLM/Portkey 等）实现。
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Quota:
    """一次实验/租户/agent 的预算配额。"""

    max_tokens: Optional[int] = None
    max_calls: Optional[int] = None
    max_cost: Optional[float] = None


@dataclass
class Usage:
    """累计用量（用于成本归因）。"""

    tokens: int = 0
    calls: int = 0
    cost: float = 0.0
    cache_hits: int = 0
    degradations: int = 0


class CachePolicy(ABC):
    """缓存策略契约：判断某请求能否命中缓存、如何取值。"""

    @abstractmethod
    def lookup(self, key: str) -> Optional[Any]:
        """按缓存键查值；未命中返回 None。"""
        ...

    @abstractmethod
    def store(self, key: str, value: Any) -> None:
        """写入缓存（key 由实现决定：精确/语义/结果）。"""
        ...


class DegradationPolicy(ABC):
    """降级策略契约：预算/截止/限流时选择“更便宜”的引擎路径。"""

    @abstractmethod
    def degrade(self, context: Any, reason: str) -> str:
        """返回降级后的目标引擎 kind（如 llm→rulellm→rule）。"""
        ...


class ScalePolicy(ABC):
    """规模化策略总契约：组合引擎配比、活跃子集/抽样、缓存、降级、配额。"""

    @abstractmethod
    def engine_mix(self, agent_id: str, round_num: int) -> str:
        """返回某 agent 本轮应使用的引擎 kind（用于路由）。"""
        ...

    @abstractmethod
    def quota(self, scope: str) -> Quota:
        """返回某作用域的预算配额。"""
        ...

    @abstractmethod
    def usage(self, scope: str) -> Usage:
        """返回某作用域的累计用量。"""
        ...
