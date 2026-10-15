"""AgentRuntime 契约。

定位：
    平台中所有 agent 的统一**递归**抽象。叶子 agent 与复合 agent 实现同一契约，
    因此复合 agent 可以任意嵌套（children() 递归），且对外只表现为“一个 agent”。

职责边界：
    - 只管「观察 → 决策 → 行动 → 成交后钩子」的生命周期与递归组合。
    - 不管“谁决定让它动”（见 activation/base.py）、“什么时候推进”（见 runtime/base.py）、
      “怎么通信”（见 message/base.py）、“怎么存状态”（见 state/base.py）。

实现规范：
    - 抽象方法必须实现；带默认值的钩子可选择性 override。
    - 实现类不得改动本契约的签名；新增能力放到实现类自身。
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Decision:
    """agent 在某一时刻产出的**决策结果**（DecisionEngine 的输出，尚未变成世界动作）。

    字段：
        action:   动作类型（如 buy / sell / hold / post / follow），领域语义由使用者定义。
        payload:  动作载荷（数量、价格、文本等），结构由领域约定。
        confidence: 置信度（0~1，可空；规则决策可省略）。
        evidence:  决策依据/溯源引用（可空，用于审计）。
    """

    action: str
    payload: Dict[str, Any] = field(default_factory=dict)
    confidence: Optional[float] = None
    evidence: Optional[Any] = None


@dataclass
class Action:
    """由 Decision 转换而来、面向“世界/市场/环境”的**最终动作**。

    字段：
        action_type: 动作类型（保留与 Decision.action 一致或进一步归一化）。
        payload:     动作载荷。
        source_id:   发起者身份（用于审计与路由）。
    """

    action_type: str
    payload: Dict[str, Any] = field(default_factory=dict)
    source_id: str = ""


class AgentRuntime(ABC):
    """统一递归 agent 抽象。

    每个 agent（叶子或复合）都实现本接口。复合 agent 的 children() 返回其子 agent，
    叶子返回空表；aggregate() 用于把子结果汇总成父级决策依据。

    契约不变式：
        - decide() 应幂等：相同内部状态应产出相同 Decision（LLM 路径由缓存/温度控制保证）。
        - act() 只把 Decision 转成 Action，不得再“思考”。
        - on_fill() 是唯一允许的成交后状态维护钩子（对应既有 MASim 契约）。
    """

    @property
    @abstractmethod
    def identity(self) -> str:
        """返回 agent 唯一标识（与 Registry 中的身份一致）。"""
        ...

    @abstractmethod
    async def observe(
        self, observation: Any, prev_result: Optional[Any] = None
    ) -> None:
        """把外部观察写入内部状态；本方法**不产生决策**。

        参数：
            observation: 本轮观察（含本地状态 + 收到的消息）。
            prev_result: 上一步结果（多步回合时传入，可为空）。
        副作用：更新内部状态。
        """
        ...

    @abstractmethod
    async def decide(self) -> Decision:
        """基于当前内部状态产出决策。

        返回：Decision（尚未执行的动作意图）。
        约定：由 DecisionEngine 具体执行（见 decision/base.py）。
        """
        ...

    @abstractmethod
    async def act(self, decision: Decision) -> Action:
        """把 Decision 转成面向世界的 Action（纯转换，不重新决策）。"""
        ...

    def on_fill(self, action: str, quantity: float, price: float) -> None:
        """成交后钩子（默认无操作）。

        仅交易型 agent 需要 override；用于 VWAP / cost-basis 等逐笔状态维护。
        调用时机：框架完成校验并更新 cash/position **之后**、且仅调用一次。
        """
        return None

    @abstractmethod
    def children(self) -> List["AgentRuntime"]:
        """返回子 agent 列表。

        叶子返回空表；复合返回其直接子 agent。递归深度由实现自行约束。
        """
        ...

    @abstractmethod
    def aggregate(self, child_results: List[Any]) -> Any:
        """把子 agent 的决策结果汇总为父级决策依据（可插拔聚合）。

        参数：child_results 为 children() 对应顺序的每个子结果（结构见 composite/base.py）。
        返回：聚合摘要（统计量 / 摘要文本 / 结构化对象）。
        """
        ...
