"""MessageBus（内部消息）契约。

定位：
    平台内部的高频通信（同集群/同进程）。沿用三层模型：
        Info（业务内容）→ Message（加路由/时间戳）→ SimPacket（可记录可传输的编码包）。

职责边界：
    - 只管内部消息；跨系统/外部/工具走 ProtocolBridge（复用 A2A/MCP/AG-UI），不在本契约内。
    - 支持聚合消息与兴趣路由（规模化的关键，见 07-communication-and-protocols.md）。
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List


class MessagePriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Info:
    """Player 层业务内容（agent 产生/消费的原始内容，领域语义由使用者定义）。"""

    payload: Any
    kind: str = "generic"
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Message:
    """Proxy 层路由消息：在 Info 之上加入发送者/接收者/时间/优先级。"""

    sender_id: str
    recipient_id: str
    info: Info
    round_num: int = 0
    priority: MessagePriority = MessagePriority.NORMAL
    seq: int = 0  # 幂等去重用


@dataclass
class SimPacket:
    """Channel 层可记录、可传输的编码包（wire 层）。"""

    encoded: Any
    routing: Dict[str, Any] = field(default_factory=dict)


class RoutePolicy(ABC):
    """消息路由策略契约：决定一条消息投递给哪些目标（含兴趣路由/聚合）。"""

    @abstractmethod
    def targets(self, message: Message) -> List[str]:
        """返回该消息应投递的目标 agent id 列表。"""
        ...


class MessageBus(ABC):
    """内部消息总线契约。"""

    @abstractmethod
    def publish(self, info: Info, sender_id: str, target_ids: List[str],
                round_num: int = 0, priority: MessagePriority = MessagePriority.NORMAL) -> None:
        """把一条 Info 投递给一组目标（构造 Message 后交给 deliver）。"""
        ...

    @abstractmethod
    def deliver(self, message: Message) -> None:
        """把一条已路由 Message 编码为 SimPacket 并送达目标。

        幂等性：同一 seq 重复投递不重复消费。
        """
        ...

    @abstractmethod
    def receive(self, agent_id: str) -> List[Info]:
        """取出某 agent 当前已到达、尚未消费的消息（消费一次）。"""
        ...
