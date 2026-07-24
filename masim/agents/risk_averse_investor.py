"""risk-averse-investor — Variance-conditioned Markowitz rebalancer.

Canonical implementation of the ``risk-averse-investor`` archetype documented
in ``examples/AGENT_POOL/finance/risk-averse-investor.md``. Sets a target
position inversely proportional to price variance, and rebalances toward it
each round.

Theoretical basis:
    Markowitz (1952) — Portfolio Selection (mean–variance optimisation).
    Tobin (1958) — Liquidity preference and asset allocation.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    variance   = Var(price_history[-lookback:])   (floor at 1e-4)
    target_qty = k / variance * cash / price
    raw_qty    = (target_qty - position) * adjustment_rate
    quantity   = clip(round(raw_qty), -20, +20)

    Cold-start guard: hold while price history is shorter than lookback.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``k``               : float — risk tolerance constant (default 0.5).
    * ``lookback``        : int > 0 — variance window (default 5).
    * ``adjustment_rate`` : float in (0, 1] — rebalancing speed (default 0.30).
    * ``max_trade``       : int > 0 — hard clip on |quantity| (default 20).
"""

from __future__ import annotations

from typing import Any, Dict, List

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


def _variance(xs: List[float]) -> float:
    n = len(xs)
    if n < 2:
        return 0.0
    mean = sum(xs) / n
    return sum((x - mean) ** 2 for x in xs) / n


class RuleRiskAverseInvestor(CanonicalRulePlayer):
    STRATEGY = "risk-averse-investor"
    DISPLAY_NAME = "Variance-Conditioned Risk-Averse Investor"
    SUMMARY = (
        "Sets a mean-variance target position and partially rebalances each "
        "tick (Markowitz 1952; Tobin 1958)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["k"] = float(extras.get("k", 0.5))
        self.state.custom_state["lookback"] = int(extras.get("lookback", 5))
        self.state.custom_state["adjustment_rate"] = float(
            extras.get("adjustment_rate", 0.30)
        )
        self.state.custom_state["max_trade"] = int(extras.get("max_trade", 20))
        # Local rolling window — independent from the auto-provisioned
        # HistoryBuffer (which only exists when record_path is set).
        self.state.custom_state["local_price_history"] = []

    def on_market_data(self, market_data: Dict[str, Any]) -> None:
        history: List[float] = self.state.custom_state["local_price_history"]
        history.append(float(market_data["price"]))
        # Keep a bounded window sized to at most 4x the lookback.
        lookback = self.state.custom_state["lookback"]
        cap = max(lookback * 4, lookback + 1)
        if len(history) > cap:
            del history[: len(history) - cap]

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        cs = self.state.custom_state
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )

        history: List[float] = cs["local_price_history"]
        lookback = cs["lookback"]
        # Cold-start guard from the profile.
        if len(history) < lookback:
            return hold
        if state.price <= 0:
            return hold

        window = history[-lookback:]
        variance = _variance(window)
        if variance <= 0.0:
            variance = 1e-4

        target_qty = cs["k"] / variance * state.cash / state.price
        raw_qty = (target_qty - state.position) * cs["adjustment_rate"]
        quantity = int(round(raw_qty))
        max_trade = cs["max_trade"]
        if quantity > max_trade:
            quantity = max_trade
        elif quantity < -max_trade:
            quantity = -max_trade

        if quantity > 0:
            return InvestorOrder.buy(
                quantity=float(quantity),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if quantity < 0:
            return InvestorOrder.sell(
                quantity=float(-quantity),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMRiskAverseInvestor(CanonicalLLMPlayer):
    STRATEGY = "risk-averse-investor"
    DEFAULT_SYS_PROMPT = """\
You are a risk-averse mean-variance investor. You size your target
position inversely to recent price variance: when volatility is low you
scale up, when it rises you scale down. You do not swing your entire
portfolio at once — you rebalance a fraction of the gap toward the target
each round.

Output format:
<analysis>state how recent volatility affects your target and rebalancing move.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}.
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Rebalance partially toward a variance-scaled target position; be more
conservative when recent volatility is high.
"""


__all__ = ["RuleRiskAverseInvestor", "LLMRiskAverseInvestor"]
