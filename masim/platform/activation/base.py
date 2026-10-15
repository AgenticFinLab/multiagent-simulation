"""Activation（激活）契约。

定位：
    平台一等模块：决定“每一轮/每一层哪些 agent 真正需要行动”，并下发激活信号。
    这是规模控制的核心入口（谁动 → 谁调 LLM）。

职责边界：
    - 只管“谁动、给多少预算、为什么动”，不管“怎么决策”（decision）。
    - 只管“发什么信号”，不管“时间怎么推进”（runtime）。
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ActivationSignal:
    """发给某个 agent 的激活信号（领域无关）。

    字段：
        round_num: 逻辑轮次。
        level:     拓扑层级。
        agent_id:  目标 agent。
        reason:    激活原因（周期 / 事件 / 阈值 / 随机 / 抽样）。
        budget:    本轮给该 agent 的预算上限（token/次数/成本）。
        deadline:  本轮决策截止时间（可空，交给 runtime 的同步策略使用）。
    """

    round_num: int
    level: int
    agent_id: str
    reason: str
    budget: Optional[Any] = None
    deadline: Optional[Any] = None


@dataclass
class BarrierSignal:
    """同步屏障信号：用于通知“本层/本轮进入/离开屏障”。"""

    round_num: int
    level: int
    opened: bool  # True=屏障开启（等待集合建立），False=屏障关闭（可进入下一层）


@dataclass
class DeadlineSignal:
    """截止信号：用于通知“某批决策已到截止时间”。"""

    round_num: int
    level: int
    expired_agent_ids: List[str] = field(default_factory=list)


class ActivationPolicy(ABC):
    """单个 agent 的激活策略（可插拔、可组合）。

    实现只回答“是否激活 + 给多少预算”，不执行决策。
    """

    @abstractmethod
    def evaluate(
        self, agent_id: str, round_num: int, level: int, context: Any
    ) -> Optional[ActivationSignal]:
        """评估某 agent 本轮是否激活。

        返回：ActivationSignal 表示激活；None 表示跳过（走默认/规则/上一轮）。
        约束：本方法应无副作用、可复算（同输入同输出）。
        """
        ...


class ActivationController(ABC):
    """激活控制器：统一评估一批 agent，决定本轮激活集合。

    职责：
        1. 为每个 agent 选取其 ActivationPolicy。
        2. 在预算约束下执行分层抽样（小群体保底）。
        3. 产出本轮 ActivationSignal 列表。
    """

    @abstractmethod
    def select(
        self,
        agent_ids: List[str],
        round_num: int,
        level: int,
        context: Any,
        max_activated: Optional[int] = None,
    ) -> List[ActivationSignal]:
        """从候选 agent 中选出本轮应激活的集合。

        参数：
            agent_ids:    本层全部候选 agent。
            round_num/level: 逻辑时间。
            context:      环境上下文（用于事件/阈值策略）。
            max_activated: 本轮激活数量上限（超限时抽样）。
        返回：被激活 agent 的 ActivationSignal 列表（未返回者本轮跳过）。
        """
        ...
