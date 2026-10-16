"""SharedState（共享环境状态 / 世界黑板）契约。

定位：
    领域无关的“共享变量层”。价格、社交图、感染人数等都可放进这里。
    具体领域规则（怎么撮合、怎么传播）由使用者以 agent/规则函数挂载，本契约只提供读写与版本。

职责边界：
    - 只提供「读 / 写 / 版本 / 快照」的通用机制。
    - 不定义任何领域字段或规则。
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class WorldVersion:
    """共享状态的版本标记（用于因果/幂等/审计）。"""

    round_num: int
    level: int
    seq: int = 0


class SharedState(ABC):
    """共享环境状态契约。"""

    @abstractmethod
    def get(self, key: str) -> Any:
        """读取一个共享变量；不存在时抛 KeyError。"""
        ...

    @abstractmethod
    def set(self, key: str, value: Any, version: WorldVersion) -> None:
        """写入一个共享变量（携带版本，用于冲突/幂等判定）。"""
        ...

    @abstractmethod
    def version(self) -> WorldVersion:
        """返回当前全局版本。"""
        ...

    @abstractmethod
    def snapshot(self) -> Dict[str, Any]:
        """返回全部共享变量的浅快照。"""
        ...
