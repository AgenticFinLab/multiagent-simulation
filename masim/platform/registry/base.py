"""Registry（身份 / 分组 / 发现 / 隔离）契约。

定位：
    平台的“命名与发现”层：agent 身份、分组、命名空间、隔离键的统一来源。

职责边界：
    - 只回答“谁是谁、属于哪个组/租户、怎么发现”。
    - 不负责消息投递（message）与状态存储（state），只为它们提供稳定身份。
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class IsolationKey:
    """多租户隔离键：同一物理集群内切分实验/租户/场景。"""

    run_id: str
    scenario: str = ""
    tenant: str = ""
    mechanism: str = ""

    def scope(self) -> str:
        """返回稳定作用域字符串（用于 StateStore/MessageBus 的隔离）。"""
        return f"{self.run_id}:{self.scenario}:{self.tenant}:{self.mechanism}"


class Registry(ABC):
    """身份与发现契约。"""

    @abstractmethod
    def register(self, agent_id: str, group: str, isolation: IsolationKey) -> None:
        """注册一个 agent 的身份与分组。"""
        ...

    @abstractmethod
    def lookup(self, agent_id: str) -> Optional[IsolationKey]:
        """按 id 查其隔离键；不存在返回 None。"""
        ...

    @abstractmethod
    def members(self, group: str, isolation: IsolationKey) -> List[str]:
        """返回某分组在某隔离作用域下的成员 id 列表。"""
        ...

    @abstractmethod
    def discover(self, agent_id: str) -> Dict[str, Any]:
        """返回某 agent 的元信息（能力、协议入口、分组等），供 A2A/路由发现。"""
        ...
