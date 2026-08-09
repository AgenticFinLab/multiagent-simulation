"""convergence-trader — Uninformed noise trader on policy-convergence beliefs.

Canonical implementation of the ``convergence-trader`` archetype documented
in ``masim/agents/defines/finance/convergence-trader.md``. Places random
directional trades with a fixed per-tick probability — provides noise-trader
liquidity and can be wrong-footed by fundamental shifts.

Theoretical basis:
    Svensson (1992) — target-zone / ERM convergence trades.
    Kyle (1985) — noise traders as the structural cover for informed flow.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    u ~ Uniform(0, 1)
    If u > trade_probability: hold.
    Else:
        direction ~ Bernoulli(0.5) → buy or sell
        quantity  ~ UniformInteger(min_quantity, max_quantity)
        Emit direction × quantity (cash / position clipping handled by base).

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``trade_probability`` : float in (0, 1) — per-tick trade probability
                              (default 0.30).
    * ``min_quantity``      : int > 0 — minimum trade quantity (default 100).
    * ``max_quantity``      : int > 0 — maximum trade quantity (default 500).
"""

from __future__ import annotations

import random
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleConvergenceTrader(CanonicalRulePlayer):
    STRATEGY = "convergence-trader"
    DISPLAY_NAME = "Convergence Trader (Uninformed Capital)"
    SUMMARY = (
        "Uninformed ERM-style convergence trader supplying random noise "
        "order flow (Svensson 1992; Kyle 1985)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["trade_probability"] = float(
            extras.get("trade_probability", 0.30)
        )
        self.state.custom_state["min_quantity"] = int(extras.get("min_quantity", 100))
        self.state.custom_state["max_quantity"] = int(extras.get("max_quantity", 500))

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        p_trade = self.state.custom_state["trade_probability"]
        if random.random() > p_trade:
            return hold

        min_q = self.state.custom_state["min_quantity"]
        max_q = self.state.custom_state["max_quantity"]
        quantity = float(random.randint(min_q, max_q))
        if quantity < 1:
            return hold

        factory = InvestorOrder.buy if random.random() < 0.5 else InvestorOrder.sell
        return factory(
            quantity=quantity,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMConvergenceTrader(CanonicalLLMPlayer):
    STRATEGY = "convergence-trader"
    DEFAULT_SYS_PROMPT = """\
You are an uninformed convergence trader in the currency / equity market.
You participate on vague policy-convergence beliefs rather than fundamentals;
your directional views are essentially random. You trade only occasionally
and in modest size — most rounds you stand aside.

Output format:
<analysis>brief reasoning (1-2 sentences)</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Decide: hold most rounds, or place a small random directional bet on
policy convergence.
"""


__all__ = ["RuleConvergenceTrader", "LLMConvergenceTrader"]
