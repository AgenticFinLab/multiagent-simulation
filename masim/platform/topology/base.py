"""Topology（交互拓扑）契约。

定位：
    描述“谁与谁交互、按什么层级推进”。领域无关：市场/社交都只是这张有向图上的一个实例。

职责边界：
    - 只回答“谁跟谁相连、层级怎么分、怎么分组/hub”。
    - 不实现任何领域规则（撮合/传播由使用者以 agent/规则函数挂载）。
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Edge:
    """一条有向交互边。"""

    source: str
    target: str
    kind: str = "peer"  # peer / broadcast / hub / group
    meta: Dict[str, Any] = field(default_factory=dict)


class Topology(ABC):
    """交互拓扑契约。"""

    @abstractmethod
    def get_execution_levels(self) -> List[List[str]]:
        """返回按因果顺序划分的执行层级（每层是 agent id 列表）。

        约定：同层并行、跨层串行；这是 Scheduler 推进的直接依据。
        """
        ...

    @abstractmethod
    def neighbors(self, agent_id: str) -> List[str]:
        """返回某 agent 的直接可达目标（供消息路由使用）。"""
        ...

    @abstractmethod
    def add_edge(self, edge: Edge) -> None:
        """增/改一条交互边（动态拓扑时使用；改动后需使层级缓存失效）。"""
        ...

    @abstractmethod
    def invalidate_levels_cache(self) -> None:
        """使层级缓存失效（动态拓扑改动后必须调用）。"""
        ...
