"""StateStore（状态 / 存储 / 持久化）契约。

定位：
    agent 状态、共享世界状态、快照与断点续跑的统一抽象。

职责边界：
    - 冷/温/热三级由实现自行映射到内存/KV/对象存储/向量库。
    - 多租户隔离通过 scope(isolation_key) 提供作用域视图。
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class Checkpoint:
    """一次快照描述（不含快照数据本身，只给定位信息）。"""

    round_num: int
    level: int
    timestamp: str = ""
    meta: Dict[str, Any] = field(default_factory=dict)


class StateStore(ABC):
    """状态存储契约。"""

    @abstractmethod
    def save(self, agent_id: str, state: Any) -> None:
        """保存某 agent 的当前状态（热/温/冷由实现决定）。"""
        ...

    @abstractmethod
    def load(self, agent_id: str) -> Any:
        """读取某 agent 的最近状态；不存在时抛 KeyError。"""
        ...

    @abstractmethod
    def append_record(self, agent_id: str, round_num: int, record: Any) -> None:
        """追加一条逐轮记录（追加式，不覆盖历史）。"""
        ...

    @abstractmethod
    def checkpoint(self, round_num: int, level: int) -> Checkpoint:
        """对当前全局状态做一次快照，返回快照定位信息。"""
        ...

    @abstractmethod
    def restore(self, checkpoint: Checkpoint) -> None:
        """从快照恢复状态（用于断点续跑/time-travel）。"""
        ...

    @abstractmethod
    def scope(self, isolation_key: str) -> "StateStore":
        """返回按 isolation_key 隔离的视图（多租户隔离）。"""
        ...
