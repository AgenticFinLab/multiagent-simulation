"""Runtime（时钟 / 同步策略 / 调度器）契约。

定位：
    平台的时间与调度核心。三者职责分离：
        Clock     —— 只维护逻辑时间 round/level/step 与耗时统计；
        SynchronizationPolicy —— 只回答“本轮/本层要不要等、等谁”；
        Scheduler —— 把 Clock + SyncPolicy + Activation + 四阶段串成一轮循环。

设计原则（D6）：
    平台只定义机制，不替使用者决定策略；等待/异步/降级由 SynchronizationPolicy 表达。
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class LogicalTime:
    """逻辑时间（非墙钟时间）：模拟世界只认这个。"""

    round: int = 0
    level: int = 0
    step: int = 0


@dataclass
class ClockMetrics:
    """一轮/一步的耗时统计（性能观测用，与逻辑时间无关）。"""

    last_duration_ms: float = 0.0
    total_duration_ms: float = 0.0
    count: int = 0


class Clock(ABC):
    """逻辑时钟契约：推进逻辑时间 + 记录耗时。"""

    @property
    @abstractmethod
    def now(self) -> LogicalTime:
        """返回当前逻辑时间。"""
        ...

    @abstractmethod
    def tick_round(self) -> None:
        """推进一轮：round += 1，level/step 归零。"""
        ...

    @abstractmethod
    def tick_level(self) -> None:
        """推进一层：level += 1。"""
        ...

    @abstractmethod
    def tick_step(self) -> None:
        """推进一步：step += 1。"""
        ...

    @abstractmethod
    def metrics(self) -> ClockMetrics:
        """返回当前耗时统计。"""
        ...


class SynchronizationPolicy(ABC):
    """同步策略契约：决定“本轮/本层怎么等”。

    默认实现只提供 strict（等全部完成）；deadline / nonblocking 按需继承实现。
    """

    @abstractmethod
    def should_wait(
        self, round_num: int, level: int, pending_agent_ids: List[str]
    ) -> bool:
        """判断是否应继续等待 pending_agent_ids 完成。

        返回：True=继续等待（屏障不放开）；False=不再等待（按策略处置未完成者）。
        """
        ...


class Scheduler(ABC):
    """轮循环调度器契约：把各模块串成一轮执行。

    一轮流程（契约规定，实现可细分）：
        Clock.tick_round() → 对每个拓扑层级 level：
            Activation.select(...) → AgentRuntime.decide()/act()（被激活者）
            → MessageBus.deliver(...) → StateStore.checkpoint(...)
        其中“是否等待该层完成”由 SynchronizationPolicy 决定。
    """

    @abstractmethod
    async def run_round(self, round_num: int) -> Dict[str, Any]:
        """执行一整轮，返回本轮结果摘要（round/level/产物引用等）。"""
        ...
